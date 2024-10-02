from services import model

def get_result_df(csv_path=None, txt_path=None, pic_path=None):
    if csv_path:
        model.get_reviews_from_csv(path=csv_path)
        model.reviews = model.reviews_df['0'].to_list()
    elif txt_path:
        model.reviews = model.get_reviews_from_txt(path=txt_path)
    model.get_clusters()
    model.get_final_clusters()
    model.generate_result_csv()
    df_result = model.final_clusters_df
    if pic_path:
        model.save_clouds_pic(pic_path)
    return df_result.drop(columns=['Sentences_vectors'])
