import streamlit as st
import pandas as pd


@st.cache_data
def load_data():
    return pd.read_csv("data/anime.csv")


def main():
    df = load_data()

    total_anime = df.shape[0]
    print(total_anime)

    if "displayed_anime" not in st.session_state:
        st.session_state.displayed_anime = []
    if "current_anime" not in st.session_state:
        st.session_state.current_anime = df.sample(5)
    if "scores" not in st.session_state:
        st.session_state.scores = {}

    progress = len(st.session_state.displayed_anime) / total_anime
    st.progress(progress)

    for idx, row in st.session_state.current_anime.iterrows():
        st.image(row["image_url"], width=200)
        st.write(row["name"])
        st.session_state.scores[row["anime_id"]] = st.slider(
            f"スコアをつけてください ({row['name']})", 0, 10, 0, key=row["anime_id"]
        )

    # 次へボタンが押されたら、スコアを保存して次の5つのアニメを表示
    if st.button("次へ"):
        st.session_state.displayed_anime.extend(st.session_state.current_anime["anime_id"].tolist())
        available_animes = df[~df["anime_id"].isin(st.session_state.displayed_anime)]
        num_to_display = min(5, available_animes.shape[0])

        if num_to_display > 0:
            st.session_state.current_anime = available_animes.sample(num_to_display)
            st.experimental_rerun()
        else:
            # すべてのアニメが表示されたら、ダウンロードリンクを表示
            st.write("評価が完了しました！ありがとうございます！")
            st.write("評価結果をダウンロード")
            scores_df = pd.DataFrame(st.session_state.scores.items(), columns=["anime_id", "score"])
            # ダウンロードリンクを表示
            csv_scores = scores_df.to_csv(index=False)
            st.download_button("ダウンロード", csv_scores, "scores.csv", "text/csv")
            # 実行を停止
            st.stop()


if __name__ == "__main__":
    main()
