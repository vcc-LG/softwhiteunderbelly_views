from bs4 import BeautifulSoup
import matplotlib.pyplot as plt


def get_soup():
    print("Parsing HTML with bs4")
    with open("./data/swu.html", "r") as f:
        contents = f.read()
    return BeautifulSoup(contents, "html.parser")


def process_view_count(view_count_element):
    views_as_words = view_count_element.contents[0].split(" ")[0]
    view_count = None
    if "K" in views_as_words:
        val_split = views_as_words.split("K")
        decimal_split = val_split[0].split(".")
        thousands = int(decimal_split[0])
        hundreds = 0
        if len(decimal_split) == 2:
            hundreds = int(decimal_split[1])
        view_count = (thousands * 1000) + (hundreds * 100)
    elif "M" in views_as_words:
        val_split = views_as_words.split("M")
        decimal_split = val_split[0].split(".")
        millions = int(decimal_split[0])
        hundred_thousands = 0
        if len(decimal_split) == 2:
            hundred_thousands = int(decimal_split[1])
        view_count = (millions * 1000000) + (hundred_thousands * 100000)
    else:
        view_count = int(views_as_words)
    return view_count


def process_video_title(element):
    title = element.contents[0]
    words = []
    title_words = title.split(" ")
    for word in title_words:
        if "-" in word:
            [words.append(x) for x in word.split("-")]
        else:
            words.append(word)
    return words


def process_page(soup):
    video_title_els = soup.find_all(
        "a", class_="yt-simple-endpoint style-scope ytd-grid-video-renderer"
    )
    print(f"Found {len(video_title_els)} videos")
    data = []
    for element in video_title_els:
        if "Soft White Underbelly" in element["aria-label"]:
            title_words = process_video_title(element)
            views = process_view_count(
                element.parent.findNext("div").find(
                    "span", class_="style-scope ytd-grid-video-renderer"
                )
            )

            data.append({"title": title_words, "views": views})
    print(f"Finished parsing data")
    return data


def group_dict_data(dict_array):
    print(f"Grouping data")
    unique_title_words = set(val for dic in dict_array for val in dic["title"])
    data = []
    for word in unique_title_words:
        if word:
            if word not in ["", "interview", "The", "the", "up)", "(follow", "and"]:
                videos = []
                for element in dict_array:
                    if word in element["title"]:
                        videos.append(element)
                total_views = sum([i["views"] for i in videos])
                data.append(
                    {
                        "word": word,
                        "videos": videos,
                        "total_views": total_views,
                        "num_videos": len(videos),
                    }
                )
    print(f"Finished grouping data")
    return data


def sort_data_dict(data_dict, sort_key):
    return sorted(data_dict, key=lambda d: d[sort_key], reverse=True)


def plot_video_count_plot(grouped_data, sort_key):
    print(f"Saving video count plot")
    plt.figure(figsize=(10, 3))
    plt.style.use("ggplot")
    words = [x["word"] for x in grouped_data][0:10]
    views = [x["num_videos"] for x in grouped_data][0:10]
    words_pos = [i for i, _ in enumerate(words)]
    plt.bar(words, views, color="green")
    plt.ylabel("Number of videos")
    plt.title("Number of videos for popular title words in SWU videos")
    plt.xticks(words_pos, words)
    plt.savefig(f"num_videos_sort_key_{sort_key}.png")


def plot_view_count_plot(grouped_data, sort_key):
    print(f"Saving view count plot")
    plt.figure(figsize=(10, 3))
    plt.style.use("ggplot")
    words = [x["word"] for x in grouped_data][0:10]
    views = [x["total_views"] for x in grouped_data][0:10]
    words_pos = [i for i, _ in enumerate(words)]
    plt.bar(words, views, color="green")
    plt.ylabel("Total view count")
    plt.title("Total view count for popular title words in SWU videos")
    plt.xticks(words_pos, words)
    plt.savefig(f"total_views_sort_key_{sort_key}.png")


def perform():
    soup = get_soup()
    data = process_page(soup)
    grouped_data = group_dict_data(data)

    sort_keys = ["total_views", "num_videos"]
    for sort_key in sort_keys:
        sorted_data = sort_data_dict(grouped_data, sort_key)
        plot_view_count_plot(sorted_data, sort_key)
        plot_video_count_plot(sorted_data, sort_key)


if __name__ == "__main__":
    perform()
