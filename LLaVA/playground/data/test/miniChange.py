import io

import pandas as pd, requests, os
from PIL import Image
df = pd.read_csv('../../data/true_use/full-data-filter-lablel-utf8.csv')         # 包含 nlp, content, img_url
os.makedirs('../data/images', exist_ok=True)
headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Referer': 'https://m.weibo.cn/',
            'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
            'Cookie':'BIDUPSID=A21268228056FA3048029AC3B2C59256; PSTM=1720860095; BAIDUID=A21268228056FA304031695B25DCBAF7:FG=1; MCITY=-154%3A; BDUSS=1DOGRjNkFoQ21OVGFvYTJkUjF5Vmp3dS1jV1RKRUxxSG5keTNGaVM2VDhocUZuSVFBQUFBJCQAAAAAAAAAAAEAAAA24h3OTGlOaUFuMTYwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPz5eWf8-XlnTS; BDUSS_BFESS=1DOGRjNkFoQ21OVGFvYTJkUjF5Vmp3dS1jV1RKRUxxSG5keTNGaVM2VDhocUZuSVFBQUFBJCQAAAAAAAAAAAEAAAA24h3OTGlOaUFuMTYwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAPz5eWf8-XlnTS; BDORZ=FFFB88E999055A3F8A630C64834BD6D0; BAIDUID_BFESS=A21268228056FA304031695B25DCBAF7:FG=1; ZFY=k0RugYVvEqP1hyItWRkw6QQw:AXy5AqwB:AhaXd6xfyJs:C; H_WISE_SIDS_BFESS=61027_60853_61491_61530_61567_61609_61639_61722_61732; BDRCVFR[uPX25oyLwh6]=mk3SLVN4HKm; H_PS_PSSID=61027_60853_61491_61530_61567_61609_61639_61732; delPer=0; PSINO=3; BAIDU_WISE_UID=wapp_1736386180072_558; arialoadData=false; H_WISE_SIDS=61027_60853_61491_61530_61567_61609_61639_61732; ab_sr=1.0.1_MzFhODg1Zjk3MjVkZThmYTlhNmVhYjQxM2VkOTUzNjI0ZjM2ZjgzNWYxYzIwMDcxOGIwYTFmZjNiZGIyYWVhZDViYjRhNjRiNWE2MmJlNDQzNWQyNmQ3M2U5N2MzMjg0YTViYjI0OTljNmFiNjZkYzNkNzA3YzE1Zjk5MGJkNjg5N2M0YjNmNWIzNDBkYmFmYmE3ZTE1ZTUzN2MwYTEyODFiZGRlMzc3MTI1YmU3NDBkZWFmNzZlN2I2MmNkMzQz; RT="z=1&dm=baidu.com&si=3d9cf5e3-d763-459c-9d8e-0baa7a6d3f85&ss=m5onhzhw&sl=2e&tt=2c0y&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf"; BA_HECTOR=8h0h2ka58g24a4a5042h2525a4u6b41jnuf4v1v'
        }
def create_blank_image(width=800, height=600, color=(255, 255, 255)):
    """生成一张指定大小和颜色的空白图片"""
    img = Image.new("RGB", (width, height), color)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

for idx, row in df.iterrows():
    url = row['img_url']
    url = str(url)
    urls = url.split(',')

    # if urls=="https://image.baidu.com/search/down?url=nan":  # 跳过空值
    #     print(f"Row {idx} has missing img_url, skipped.")
    #     continue
    try:
        url_true = urls[0]
        print(url_true)

        res = requests.get(url_true, headers=headers, timeout=10)

        if res.status_code == 200:

            with open(f"../data/images/{idx}.jpg", 'wb') as f:
                f.write(res.content)
    # except Exception as e:
    #     print(f"Failed to download {url}: {e}")
    except Exception as e:
            print(f"Failed to download {url_true}: {e}")
            blank_img_data = create_blank_image()
            with open(f"../data/images/{idx}.jpg", 'wb') as f:
                f.write(blank_img_data)
            print(f"Saved blank image for failed URL: {url_true}")