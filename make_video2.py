import sys, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_video as mv
from make_video import *  # constants and helpers

def sc(fn, k): return lambda d, t: fn(d, t * k)
def L(d, x0, y0, x1, y1, c=DIM, a=1.0): d.line((x0, y0, x1, y1), fill=mv.mix(c, a), width=3)

# ---------------------------------------------------------------- 왜 해시?
LEDGER = ["1. Alice -> Bob      1.0 BTC", "2. Bob -> Carol     0.5 BTC",
          "3. Carol -> Dave    0.2 BTC", "4. Dave -> Eve      0.1 BTC"]
LEDGER_BAD = list(LEDGER); LEDGER_BAD[1] = "2. Bob -> Carol      50 BTC"
HA = sha("\n".join(LEDGER)); HB = sha("\n".join(LEDGER_BAD))

def s_why(d, t):
    T(d, 60, 40, "왜 해시가 필요할까?", KRB(40), FG)
    R(d, (60, 130, 600, 500), PANEL, LINE, fade(t, 0.3), 16)
    T(d, 80, 145, "공유 장부 (거래 기록)", KRB(24), FG, fade(t, 0.3))
    for i, ln in enumerate(LEDGER):
        bad = i == 1 and t >= 8.0
        T(d, 80, 205 + i * 62, LEDGER_BAD[i] if bad else ln, MONO(22), RED if bad else FG, fade(t, 0.8 + i * 0.4))
    if t >= 4.5:
        a = fade(t, 4.5)
        T(d, 660, 150, "장부 전체의 지문 (SHA-256 해시)", KRB(24), ORANGE, a)
        R(d, (660, 200, 1220, 400), PANEL, ORANGE, a, 16, 3)
        arrow(d, 605, 655, 300, ORANGE, a)
        if t < 8.0:
            h, col = scramble(HA, 4.8, t), FG
        else:
            h, col = scramble(HB, 8.3, t), RED
        for line in range(2):
            hash_row(d, 690, 235 + line * 60, h[line * 32:(line + 1) * 32], MONO(28), [col] * 32, a)
    if t >= 11.5:
        T(d, 940, 450, "원본 지문과 다름!  ->  위조 발견", KRB(26), RED, fade(t, 11.5), "mm")

# ---------------------------------------------------------------- 머클 트리
TX = ["Alice -> Bob 1 BTC", "Bob -> Carol 0.5 BTC", "Carol -> Dave 0.2 BTC", "Dave -> Eve 0.1 BTC"]
TXB = list(TX); TXB[2] = "Carol -> Dave 20 BTC"
def tree(txs):
    l1 = [sha(x) for x in txs]
    l2 = [sha(l1[0] + l1[1]), sha(l1[2] + l1[3])]
    return l1, l2, sha(l2[0] + l2[1])
TA, TB = tree(TX), tree(TXB)

def s_merkle(d, t):
    T(d, 60, 40, "거래들을 해시 하나로 요약: 머클 루트", KRB(40), FG)
    bad = t >= 11.5
    tr = TB if bad else TA
    txs = TXB if bad else TX
    cx = [190, 490, 790, 1090]
    c2 = [340, 940]
    ya, yb, yc, yd = 450, 340, 230, 120
    red = lambda cond: RED if (bad and cond) else FG
    def box(x, y, w, txt, f, col, a, out=LINE):
        R(d, (x - w // 2, y, x + w // 2, y + 48), PANEL, out, a, 10, 2)
        T(d, x, y + 24, txt, f, col, a, "mm")
    a0, a1, a2, a3 = fade(t, 0.5), fade(t, 3.0), fade(t, 5.5), fade(t, 8.0)
    for i in range(4):
        L(d, cx[i], ya, cx[i], yb + 48, RED if (bad and i == 2) else DIM, min(a0, a1))
        L(d, cx[i], yb, c2[i // 2], yc + 48, RED if (bad and i // 2 == 1) else DIM, min(a1, a2))
    for k in range(2):
        L(d, c2[k], yc, 640, yd + 48, RED if (bad and k == 1) else DIM, min(a2, a3))
    for i in range(4):
        box(cx[i], ya, 250, txs[i], MONO(16), red(i == 2), a0, RED if (bad and i == 2) else LINE)
        box(cx[i], yb, 190, tr[0][i][:8] + "…", MONO(20), red(i == 2), a1, RED if (bad and i == 2) else LINE)
    for k in range(2):
        box(c2[k], yc, 190, tr[1][k][:8] + "…", MONO(20), red(k == 1), a2, RED if (bad and k == 1) else LINE)
    box(640, yd, 210, tr[2][:8] + "…", MONO(22), RED if bad else ORANGE, a3, RED if bad else ORANGE)
    T(d, 770, yd + 24, "<- 머클 루트", KRB(22), RED if bad else ORANGE, a3, "lm")
    T(d, 640, 535, "거래 4개 -> 해시 4개 -> 해시 2개 -> 해시 1개", KR(22), DIM, a3, "mm")

# ---------------------------------------------------------------- 난이도
def s_odds(d, t):
    T(d, 60, 40, "왜 '0000' 해시를 찾기가 어려울까?", KRB(40), FG)
    T(d, 60, 112, "해시는 무작위라서, 앞자리가 0이 되길 바라며 복권처럼 계속 뽑아야 합니다", KR(24), DIM, fade(t, 0.4))
    rows = [("1개", "16번", FG), ("2개", "256번", FG), ("3개", "4,096번", FG),
            ("4개", "65,536번  <- 이 영상의 예시", ORANGE), ("8개", "약 43억 번", FG),
            ("19~20개", "약 10^23 ~ 10^24 번  <- 실제 비트코인", RED)]
    R(d, (60, 160, 1220, 232), PANEL, LINE, fade(t, 1.0), 12)
    T(d, 120, 196, "해시 앞의 0 개수", KRB(26), DIM, fade(t, 1.0), "lm")
    T(d, 460, 196, "평균 시도 횟수", KRB(26), DIM, fade(t, 1.0), "lm")
    for i, (z, n, col) in enumerate(rows):
        a = fade(t, 2.2 + i * 1.5)
        y = 250 + i * 52
        R(d, (60, y, 1220, y + 44), PANEL, col if col != FG else LINE, a, 10, 3 if col != FG else 2)
        T(d, 120, y + 22, z, KRB(26), col, a, "lm")
        T(d, 460, y + 22, n, KR(26), col, a, "lm")
    if t >= 11.5:
        T(d, 640, 596, "0이 하나 늘 때마다 평균 16배 어려워집니다.  네트워크는 약 10분에 블록 1개가 나오도록 난이도를 자동 조절합니다",
          KR(20), ORANGE, fade(t, 11.5), "mm")

# ---------------------------------------------------------------- 검증
def s_verify(d, t):
    T(d, 60, 40, "찾기는 어렵고, 확인은 쉽다", KRB(40), FG)
    R(d, (60, 130, 600, 470), PANEL, LINE, fade(t, 0.4), 16)
    T(d, 80, 148, "채굴자", KRB(28), ORANGE, fade(t, 0.4))
    T(d, 80, 210, "정답을 찾기까지", KR(22), DIM, fade(t, 0.8))
    T(d, 80, 250, f"{FOUND + 1:,} 번", KRB(52), FG, fade(t, 0.8))
    T(d, 80, 340, "해시를 무수히 계산해야 했음", KR(22), DIM, fade(t, 1.4))
    if t >= 3.5:
        a = fade(t, 3.5)
        R(d, (640, 130, 1220, 470), PANEL, GREEN, a, 16, 3)
        T(d, 660, 148, "검증하는 다른 컴퓨터", KRB(28), GREEN, a)
        T(d, 660, 205, f"채굴자가 알려준 논스 {FOUND:,} 로", KR(22), DIM, a)
        T(d, 660, 238, "해시를 딱 1번만 계산해 보면", KR(22), DIM, a)
        if t >= 5.5:
            h = FOUND_H
            f = MONO(26); adv = f.getlength("0")
            z = len(h) - len(h.lstrip("0"))
            for i, ch in enumerate(h[:32]):
                T(d, 660 + i * adv, 300, ch, f, GREEN if i < z else FG, fade(t, 5.5))
            T(d, 660, 360, "0000 으로 시작 -> 통과!", KRB(30), GREEN, fade(t, 6.5))
    if t >= 8.5:
        T(d, 640, 540, "가장 먼저 찾은 채굴자가 블록을 추가하고 보상(새 비트코인 + 수수료)을 받습니다",
          KRB(24), ORANGE, fade(t, 8.5), "mm")
    if t >= 10.5:
        T(d, 640, 585, "그래서 '작업증명(Proof of Work)': 많은 계산을 했다는 증거가 곧 신뢰입니다", KR(22), DIM, fade(t, 10.5), "mm")

# ---------------------------------------------------------------- 마무리
def s_outro2(d, t):
    T(d, 640, 120, "한눈에 정리", KRB(48), FG, fade(t, 0.1), "mm")
    items = [("해시", "어떤 데이터든 고정 길이의 '지문'으로 바꾸는 단방향 함수", FG),
             ("머클 루트", "수많은 거래를 해시 하나로 요약한 값", FG),
             ("채굴", "논스를 바꿔가며 '조건에 맞는 해시'를 찾는 복권 같은 작업", ORANGE),
             ("검증", "찾기는 어렵지만 확인은 해시 1번이면 끝", FG),
             ("블록체인", "이전 블록 해시를 포함해 과거 기록 위조를 사실상 불가능하게 함", FG)]
    for i, (k, v, col) in enumerate(items):
        a = fade(t, 0.8 + i * 1.3)
        y = 200 + i * 80
        R(d, (80, y, 1200, y + 64), PANEL, col if col != FG else LINE, a, 12, 3 if col != FG else 2)
        T(d, 110, y + 32, k, KRB(28), ORANGE, a, "lm")
        T(d, 330, y + 32, v, KR(24), FG, a, "lm")

SCENES = [
    (4.5, mv.s_title, []),
    (14.5, s_why, [(0.5, "비트코인은 모든 거래를 적은 '공유 장부'를 여러 사람이 나눠 갖습니다"),
                   (4.0, "누가 몰래 숫자를 고치면 어떻게 알아챌까요? 장부 전체의 '지문'을 만들어 두면 됩니다"),
                   (8.2, "이 지문이 바로 '해시'입니다. 한 글자만 고쳐도 지문이 달라져 위조가 들통납니다")]),
    (19.0, sc(mv.s_hash, 0.68), [(0.7, "믹서기처럼 무엇을 넣든 항상 64자리(256비트)의 해시가 나옵니다"),
                                 (9.3, "이번엔 대문자 B를 소문자 b로, 딱 한 글자만 바꿔 봅니다"),
                                 (16.8, "한 글자 차이인데 해시는 완전히 다른 값이 됩니다")]),
    (15.3, sc(mv.s_props, 0.62), [(0.8, "좋은 해시 함수에는 세 가지 성질이 있습니다"),
                                  (4.5, "해시만 보고는 원래 입력을 거꾸로 알아낼 수 없습니다 (주스를 다시 과일로 못 돌리듯)"),
                                  (8.8, "입력이 조금만 달라도 결과는 예측 불가능하게 달라집니다")]),
    (15.5, s_merkle, [(0.5, "블록에는 수천 개의 거래가 들어갑니다. 먼저 거래마다 해시를 만들고"),
                      (3.2, "해시 두 개를 이어 붙여 다시 해시하는 과정을 반복하면"),
                      (8.2, "맨 위에 하나가 남습니다. 이것이 거래 전체를 대표하는 머클 루트입니다"),
                      (11.7, "거래 하나만 바뀌어도 위쪽 해시가 줄줄이 바뀌어 머클 루트가 달라집니다")]),
    (14.3, sc(mv.s_header, 0.7), [(0.5, "이제 블록 헤더에 들어가는 정보들을 모읍니다 (이전 블록 해시, 머클 루트 등)"),
                                  (6.2, "이 헤더를 SHA-256에 두 번 돌리면 블록 해시가 나옵니다"),
                                  (10.7, "채굴자가 마음대로 바꿔 볼 수 있는 값이 바로 논스(nonce)입니다")]),
    (16.5, s_odds, [(0.5, "채굴의 목표: 블록 해시가 특정 조건(앞자리가 0)을 만족하는 것"),
                    (3.0, "0이 하나 늘어날 때마다 필요한 시도 횟수가 16배씩 늘어납니다"),
                    (12.0, "그래서 실제 비트코인은 천문학적인 횟수의 해시 계산이 필요합니다")]),
    (22.0, sc(mv.s_mine, 0.75), [(0.5, "이제 직접 해 봅니다. 목표는 해시가 0000으로 시작하는 것"),
                                 (4.5, "역산이 불가능하니 논스를 바꿔가며 무작정 해시를 돌려봅니다"),
                                 (11.0, "가끔 0으로 시작하는 해시가 나오지만 0000에는 못 미칩니다 (주황색)"),
                                 (14.9, "찾았다! 조건을 만족하는 논스를 발견했습니다")]),
    (12.5, s_verify, [(0.5, "채굴자는 수많은 계산 끝에 정답을 찾았습니다"),
                      (3.7, "하지만 다른 컴퓨터는 이 정답을 해시 1번만 계산해서 확인합니다"),
                      (8.7, "가장 먼저 찾은 채굴자가 보상을 받습니다")]),
    (16.0, sc(mv.s_chain, 0.78), [(0.5, "각 블록은 앞 블록의 해시를 담고 있어 사슬처럼 이어집니다"),
                                  (6.5, "과거 거래를 하나 조작하면 그 블록의 해시가 바뀌고"),
                                  (11.0, "뒤 블록과의 연결이 끊어져 들통납니다. 이후 블록을 전부 다시 채굴해야 합니다")]),
    (9.0, s_outro2, [(5.5, "해시 하나가 비트코인의 신뢰를 만드는 핵심입니다")]),
]
mv.SCENES = SCENES
mv.TOTAL = sum(s[0] for s in SCENES)

if __name__ == "__main__":
    if sys.argv[1] == "preview":
        for gt in [float(x) for x in sys.argv[3:]]:
            mv.render(gt).save(os.path.join(sys.argv[2], f"v2_{gt:05.1f}.png"))
        sys.exit()
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                           "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium", sys.argv[1]],
                          stdin=subprocess.PIPE)
    n = int(mv.TOTAL * FPS)
    for i in range(n):
        ff.stdin.write(mv.render(i / FPS).tobytes())
    ff.stdin.close(); ff.wait()
    print("frames", n, "sec", mv.TOTAL)
