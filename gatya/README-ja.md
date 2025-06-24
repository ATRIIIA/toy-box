
[English](/gatya/README.md)  [Japanese](/gatya/README-ja.md)
## 技術仕様
<img src="https://img.shields.io/badge/-Html5-E34F26.svg?logo=html5&style=plastic"> <img src="https://img.shields.io/badge/-Css3-1572B6.svg?logo=css3&style=plastic"> <img src="https://img.shields.io/badge/-Javascript-F7DF1E.svg?logo=javascript&style=plastic">

## 目次　　
1. [プロジェクト名](#プロジェクト名)
2. [プロジェクト概要](#プロジェクトについて)
3. [使い方](#使い方)
4. [index.htmlの書き換え](#indexhtmlの書き換え)

<!-- プロジェクト名 -->
## プロジェクト名
gatya-htmlのリポジトリ

<!-- プロジェクトについて -->
## プロジェクトについて
htmlを用いたガチャ

<!-- 使い方 -->
## 使い方
1. Codeからdownload.zipをダウンロード
2. imagesフォルダーに使いたい画像を入れてください。(推奨512x512サイズのPNG)
3. [index.htmlファイルを書き換える。](#indexhtmlの書き換え)
4. index.htmlを実行してください。

<!-- index.htmlの書き換え -->
## index.htmlの書き換え
srcに画像のディレクトリを入れえてください。  
altに名前を入れてください。　例）N-1
```
<img id="img" src="images/1.png" alt="N-1">
<img id="img" src="images/1.png" alt="N-2">
```
> [!NOTE] 
> 画像はランダムに並び変えられるので  
> 1%の確率にしたい場合、99枚の画像を追加する必要があります。
