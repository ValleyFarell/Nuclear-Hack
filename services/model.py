import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sentence_transformers import SentenceTransformer, util
import yake
import re
import time
import matplotlib.patheffects as PathEffects

extractor = yake.KeywordExtractor (
    lan = "ru",     # язык
    n = 6,          # максимальное количество слов в фразе
    dedupLim = 0.8, # порог похожести слов
    top = 10        # количество ключевых слов
)

# Модель для вычисления эмбеддингов русскоязычных текстов
model = SentenceTransformer("distiluse-base-multilingual-cased")
clusters, reviews_orig, corpus_embeddings, corpus_sentences, reviews = [], [], [], [], []
final_clusters = []
reviews_df = pd.DataFrame()
final_clusters_df = pd.DataFrame()

def prepare_sentence(sentence):
    pattern = r'(?iu)\b(?:(?:(?:у|[нз]а|(?:хитро|не)?вз?[ыьъ]|с[ьъ]|(?:и|ра)[зс]ъ?|(?:о[тб]|п[оа]д)[ьъ]?|(?:.\B)+?[оаеи-])-?)?(?:[её](?:б(?!о[рй]|рач)|п[уа](?:ц|тс))|и[пб][ае][тцд][ьъ]).*?|(?:(?:н[иеа]|(?:ра|и)[зс]|[зд]?[ао](?:т|дн[оа])?|с(?:м[еи])?|а[пб]ч|в[ъы]?|пр[еи])-?)?ху(?:[яйиеёю]|л+и(?!ган)).*?|бл(?:[эя]|еа?)(?:[дт][ьъ]?)?|\S*?(?:п(?:[иеё]зд|ид[аое]?р|ед(?:р(?!о)|[аое]р|ик)|охую)|бля(?:[дбц]|тс)|[ое]ху[яйиеё]|хуйн).*?|(?:о[тб]?|про|на|вы)?м(?:анд(?:[ауеыи](?:л(?:и[сзщ])?[ауеиы])?|ой|[ао]в.*?|юк(?:ов|[ауи])?|е[нт]ь|ища)|уд(?:[яаиое].+?|е?н(?:[ьюия]|ей))|[ао]л[ао]ф[ьъ](?:[яиюе]|[еёо]й))|елд[ауые].*?|ля[тд]ь|(?:[нз]а|по)х)\b'
    low_sent = sentence.lower()
    if re.search(pattern, low_sent):
        return ''
    return re.sub(r'\s+', ' ', low_sent.strip().replace('\n', '').replace('мтс', ''), count=0)

def get_reviews_from_csv(path='REVIEWS_DB.csv'):
    global reviews_df
    reviews_df = pd.read_csv(path)

def get_reviews_from_txt(path):
  return open(path, 'r', encoding="utf8").readlines()

# Подсчет эмбеддингов для каждого ответа сотрудника с последующей кластеризацией
def get_clusters():
    global clusters, reviews_orig, corpus_embeddings, corpus_sentences, reviews, model
    # Ограничения на размер корпуса. Фиксирован для избежания перегрузки оперативной памяти
    max_corpus_size = 50000
    # Пусть корпус будет состоять из уникальных отзывов. Это можно изменить по желанию
    corpus_sentences = []
    
    reviews = list(set(reviews))
    reviews_copy = reviews
    reviews = []
    for rev in reviews_copy:
        prepared_rev = prepare_sentence(rev)
        if prepared_rev == '' or prepared_rev == ' ':
            continue
        reviews.append(prepared_rev)

    reviews_orig = reviews
    for review in reviews:
        corpus_sentences.append(review)
        if len(corpus_sentences) >= max_corpus_size:
            break
    print("Подсчет эмбеддингов. Возможно, придется подождать")
    corpus_embeddings = model.encode(corpus_sentences, batch_size=32, show_progress_bar=True, convert_to_tensor=True)
    print("Начало кластеризации")
    start_time = time.time()

    min_community_size = 1 if len(corpus_sentences) < 20 else \
                         2 if len(corpus_sentences) < 50 else \
                         3 if len(corpus_sentences) < 100 else \
                         5 if len(corpus_sentences) < 300 else \
                         10 if len(corpus_sentences) < 600 else \
                         12 if len(corpus_sentences) < 1000 else 18
    
    # Запускаем кластеризацию, предварительно определив 2 параметра
    # min_community_size: минимальное число векторов в кластере
    # threshold: порог для косинусного расстояния
    
    clusters = util.community_detection(corpus_embeddings, min_community_size=min_community_size, threshold=0.55)
    print(f"Кластеризация произведена за {time.time() - start_time:.2f} секунд")

def print_clusters():
    for i, cluster in enumerate(clusters):
        print(f"\nCluster {i + 1}, #{len(cluster)} Elements ")
        for sentence_id in cluster:
            print("\t", corpus_sentences[sentence_id])

# Извлечение ключевого словв из одного предложения
def get_keys(sentence):
  lst = extractor.extract_keywords(sentence)
  return sorted(lst, key=lambda x: x[1])

# Получение финального результата с лейблом категории
def get_final_clusters():
    global final_clusters
    final_clusters = []
    for i, cluster in enumerate(clusters):
        # print(f"\nCluster {i + 1}, #{len(cluster)} Elements ")
        cluster_maxs = []
        for sentence_id in cluster:
            keys = get_keys(corpus_sentences[sentence_id])
            if keys == []:
                cluster_maxs += [(corpus_sentences[sentence_id], 0.0)]
            else:
                cluster_maxs += [get_keys(corpus_sentences[sentence_id])[0]]
        mx = sorted(cluster_maxs, key=lambda x: x[1])[-1]
        # print(mx)
        final_clusters.append((cluster, mx[0]))

# Сохранение результата кластеризации в csv формате
def generate_result_csv():
    global final_clusters_df
    final_clusters_df = pd.DataFrame(columns=['Label', 'Sentences', 'Sentences_vectors'])
    for i, cluster in enumerate(clusters):
        sentences = []
        vectors = []
        for sentence_id in cluster:
            sentences.append(reviews_orig[sentence_id])
            vectors.append(model.encode(corpus_sentences[sentence_id])[0])
        new_row = {'Label': final_clusters[i][1], 'Sentences': sentences, 'Sentences_vectors': vectors}
        final_clusters_df = pd.concat([final_clusters_df, pd.DataFrame([new_row])], ignore_index=True)

# Визуализация кластеров
def save_clouds_pic(path):
    n_clusters = len(final_clusters)
    dimention = 2
    cov_matrix = [[100, 0], [0, 100]]
    classes_centers = np.random.multivariate_normal([0, 0], cov_matrix, n_clusters)

    def make_class(center, n_points):
        n = len(center)
        cov_matrix = np.random.rand(n, n)
        return np.random.multivariate_normal(center, cov_matrix, n_points)

    plt.figure(figsize=(10,10))
    for i in range(n_clusters):
        X = make_class(classes_centers[i], len(clusters[i]))
        color = np.random.rand(3,)
        plt.scatter(X[:, 0], X[:, 1], c=color, s=[10] * len(clusters[i]))

        txt = plt.text(np.average(X[:, 0]), np.average(X[:, 1]), final_clusters[i][1], horizontalalignment='center',
            verticalalignment='center', fontsize=(2 + 5 * np.log(len(clusters[i]) + 1)), color=color)
        txt.set_path_effects([PathEffects.withStroke(linewidth=0.5, foreground='black')])

    plt.savefig(path)
    return path