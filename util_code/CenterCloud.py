from wordcloud import WordCloud
from PIL import ImageFont

class CenteredWordCloud(WordCloud):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def generate_from_frequencies(self, frequencies, max_font_size=None):
        wordcloud_obj = super().generate_from_frequencies(frequencies, max_font_size)

        # 彻底过滤字体大小 <= 0 的词
        wordcloud_obj.layout_ = [item for item in wordcloud_obj.layout_ if item[1] > 0]
        wordcloud_obj.words_ = {word: freq for (word, freq), size, pos, orient, color in wordcloud_obj.layout_}

        if not wordcloud_obj.layout_:
            print("所有词都被过滤，词云为空，跳过居中")
            return wordcloud_obj

        valid_layout = [item for item in wordcloud_obj.layout_ if item[1] > 0]
        if not valid_layout:
            print("所有词字体大小为0，跳过居中")
            return wordcloud_obj

        max_item = max(valid_layout, key=lambda item: item[1])
        (word, freq), font_size, (row, col), orientation, color = max_item

        if font_size <= 0:
            print(f"跳过字体大小为0的词：{word}")
            return wordcloud_obj

        try:
            font = ImageFont.truetype(self.font_path, font_size)
            x0, y0, x1, y1 = font.getbbox(word)
        except Exception as e:
            print(f"[字体错误] {e}")
            return wordcloud_obj

        w = x1 - x0
        h = y1 - y0
        center_word_row = row + h / 2
        center_word_col = col + w / 2

        if self.mask is not None:
            height, width = self.mask.shape
        else:
            height, width = self.height, self.width

        center_canvas_row = height / 2
        center_canvas_col = width / 2

        shift_row = int(center_canvas_row - center_word_row)
        shift_col = int(center_canvas_col - center_word_col)

        new_layout = []
        for (wfreq, fs), (r, c), ori, colr in [(item[0], item[2], item[3], item[4]) for item in valid_layout]:
            new_layout.append(((wfreq, fs), fs, (r + shift_row, c + shift_col), ori, colr))

        wordcloud_obj.layout_ = new_layout

        return wordcloud_obj
