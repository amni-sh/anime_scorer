import streamlit as st
import pandas as pd


@st.cache_data
def load_data():
    return pd.read_csv("data/contents.csv")


def counter(score_dict: dict):
    # valueの値が0より大きい要素の数を返す
    return len([v for v in score_dict.values() if v > 0])


def search_anime(df: pd.DataFrame, query: str):
    if query:
        return df[df["name"].str.contains(query, case=False, na=False)]
    return pd.DataFrame()


def next_page():
    st.session_state.page += 1


def main():
    df = load_data()

    if "displayed_anime" not in st.session_state:
        st.session_state.displayed_anime = []
    if "current_anime" not in st.session_state:
        st.session_state.current_anime = df.sample(5)
    if "scores" not in st.session_state:
        st.session_state.scores = {}
    if "search_query" not in st.session_state:
        st.session_state.search_query = ""
    if "page" not in st.session_state:
        st.session_state.page = 0

    if st.session_state.page == 0:
        st.write("## 研究用アンケート(1/2)")
        st.write("CloudWorksから応募いただき、ありがとうございます！")
        st.write(
            "このアンケートに回答する前に、必ず、[アンケート説明書](https://docs.google.com/document/d/1pZMQ-hzRkcvdb3QtmmbjFPFsEG8yVQ63lAO-VSgK5Hg/edit)をご覧ください。"
        )
        st.write(
            "これまでのアニメの視聴数が30本に満たない場合、申し訳ありませんが、このアンケートに参加することはできません。"
        )
        st.write("説明書を読んだ後、以下のボタンを押してアンケートを開始してください。")
        st.write("アンケートに関して、何か質問がある場合は、cloudworksのメッセージ機能を使ってお知らせください。")
        st.button("開始", on_click=next_page)

    elif st.session_state.page == 1:
        rated_anime_count = counter(st.session_state.scores)
        progress = rated_anime_count / 30
        # print(rated_anime_count, progress)
        st.write(f"{min(len(st.session_state.displayed_anime), len(df))} / {len(df)}")
        st.progress(min(progress, 1.0))

        st.session_state.search_query = st.text_input("アニメ名で検索", st.session_state.search_query)
        # print(f"query: {st.session_state.search_query}, {st.session_state.current_anime}")

        if st.session_state.search_query:
            st.session_state.current_anime = search_anime(df, st.session_state.search_query)
            # print(st.session_state.current_anime)

        for idx, row in st.session_state.current_anime.iterrows():
            st.image(row["image_url"], width=200)
            st.write(row["name"])

            st.session_state.scores[row["anime_id"]] = st.slider(
                f"スコアをつけてください ({row['name']})", 0, 10, 0, key=row["anime_id"]
            )

        # 次へボタンが押されたら、スコアを保存して次の5つのアニメを表示
        if st.button("次へ"):
            st.session_state.search_query = ""
            st.session_state.displayed_anime.extend(st.session_state.current_anime["anime_id"].tolist())
            available_animes = df[~df["anime_id"].isin(st.session_state.displayed_anime)]
            num_to_display = min(5, available_animes.shape[0])

            if rated_anime_count < 30:
                if num_to_display > 0:
                    st.session_state.current_anime = available_animes.sample(num_to_display)
                    st.experimental_rerun()
                else:
                    # すべてのアニメが表示されたら、ダウンロードリンクを表示
                    st.write("評価が完了しました！ありがとうございます！")
                    st.write("評価結果をダウンロード")
                    scores_df = pd.DataFrame(st.session_state.scores.items(), columns=["anime_id", "rating"])
                    # ダウンロードリンクを表示
                    csv_scores = scores_df.to_csv(index=False)
                    st.download_button("ダウンロード", csv_scores, "scores.csv", "text/csv")
                    # 実行を停止
                    st.stop()
            else:
                st.write("評価が完了しました！ありがとうございます！")
                st.write("評価結果をダウンロード")
                scores_df = pd.DataFrame(st.session_state.scores.items(), columns=["anime_id", "rating"])
                # ダウンロードリンクを表示
                csv_scores = scores_df.to_csv(index=False)
                st.download_button("ダウンロード", csv_scores, "scores.csv", "text/csv")
                # 実行を停止
                st.stop()


if __name__ == "__main__":
    main()
