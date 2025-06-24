// 右クリックを無効化するイベントリスナーを設定
document.addEventListener('contextmenu', function(event) {
  event.preventDefault(); // デフォルトのコンテキストメニューを防止
});

// DOMの読み込み完了後に実行する処理
document.addEventListener('DOMContentLoaded', () => {
  const reel = document.querySelector('.reel'); // スロットの親要素を取得
  const container = document.getElementById("shuffle-container"); // シャッフル対象のコンテナを取得
  const items = Array.from(container.children); // コンテナ内の全子要素を配列に変換

  // 要素をランダムにシャッフルする
  const shuffled = items.sort(() => Math.random() - 0.5);

  // シャッフル後、コンテナ内の要素を再配置する
  container.innerHTML = ""; // コンテナを空にする
  shuffled.forEach(item => container.appendChild(item)); // シャッフルされた要素を再追加

  // スロットのリールをランダムな横方向位置に移動
  const randomPosition = -8000 + (Math.random() * -140); // ランダムな移動位置を計算
  reel.style.transition = 'transform 1s ease-out'; // トランジション（アニメーション）を設定
  reel.style.transform = `translateX(${randomPosition}px)`; // リールを移動

  // 移動位置をコンソールに出力 デバック用
  // console.log(randomPosition);

  // 移動後、中央に来る画像のALT情報を取得して出力
  setTimeout(() => {
    const imageWidth = 163; // 1画像の幅（ピクセル）
    const imageMargin = 13; // 画像間の余白
    const totalImageWidth = imageWidth + imageMargin; // 1画像あたりの合計幅

    const reelWidth = document.querySelector('.reel').clientWidth; // リール全体の幅を取得
    const centerOffset = (reelWidth / 2); // 画面の中央位置を計算

    // 中央に表示される画像のインデックスを計算
    const centralImageIndex = Math.round(Math.abs(randomPosition - centerOffset) / totalImageWidth);

    // リール内のすべての画像を取得
    const images = Array.from(document.querySelectorAll('.reel img'));
    
    // 中央の画像のALT属性をコンソールに出力 デバック用
    if (images[centralImageIndex]) {
      console.log('中央に来る画像ALT属性:', images[centralImageIndex].alt);
    } else {
      console.log('中央の画像を特定できませんでした。'); // 画像が見つからない場合のメッセージ
    }
  }, 1200); // アニメーション完了後の遅延時間（1.2秒）
});
