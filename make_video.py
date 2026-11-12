import hashlib, random, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1280, 720, 30
BG = (13, 17, 23); FG = (230, 237, 243); DIM = (139, 148, 158)
ORANGE = (247, 147, 26); GREEN = (63, 185, 80); RED = (248, 81, 73)
BLUE = (88, 166, 255); PANEL = (22, 27, 34); LINE = (48, 54, 61)

FD = "C:/Windows/Fonts/"
def font(n, s): return ImageFont.truetype(FD + n, s)
KR = lambda s: font("malgun.ttf", s)
KRB = lambda s: font("malgunbd.ttf", s)
MONO = lambda s: font("consola.ttf", s)

G = 1.0
def mix(c, a=1.0):
    a = max(0.0, min(1.0, a)) * G
    return tuple(int(BG[i] + (c[i] - BG[i]) * a) for i in range(3))

def T(d, x, y, s, f, c=FG, a=1.0, anc="la"):
    d.text((x, y), s, font=f, fill=mix(c, a), anchor=anc)

def R(d, box, fill=None, out=None, a=1.0, r=14, w=2):
    d.rounded_rectangle(box, radius=r, fill=mix(fill, a) if fill else None,
                        outline=mix(out, a) if out else None, width=w)

def sm(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

def fade(t, t0, dur=0.5): return sm((t - t0) / dur)

def sha(s): return hashlib.sha256(s.encode()).hexdigest()
def dsha(s): return hashlib.sha256(hashlib.sha256(s.encode()).digest()).hexdigest()

def hash_row(d, x, y, h, f, colors=None, a=1.0):
    adv = f.getlength("0")
    for i, ch in enumerate(h):
        c = colors[i] if colors else FG
        T(d, x + i * adv, y, ch, f, c, a)

def scramble(h, t0, t, speed=0.04):
    out = []
    for i, ch in enumerate(h):
        if t >= t0 + i * speed: out.append(ch)
        else: out.append(random.Random(int(t * 30) * 131 + i).choice("0123456789abcdef"))
    return "".join(out)

def arrow(d, x0, x1, y, c=DIM, a=1.0):
    d.line((x0, y, x1, y), fill=mix(c, a), width=3)
    d.polygon([(x1, y), (x1 - 12, y - 8), (x1 - 12, y + 8)], fill=mix(c, a))

# ------------------------------------------------------------------ data
H1 = sha("Hello Bitcoin"); H2 = sha("Hello bitcoin")
DIFF_BITS = bin(int(H1, 16) ^ int(H2, 16)).count("1")

BASE = "v=0x20000000|prev=00000000a3f19c|merkle=7d3c91be|time=1762939800|bits=0x1d00ffff|nonce="
FOUND = 0
while not dsha(BASE + str(FOUND)).startswith("0000"): FOUND += 1
FOUND_H = dsha(BASE + str(FOUND))

def mine(prev, data, z=2):
    n = 0
    while not dsha(f"{prev}|{data}|{n}").startswith("0" * z): n += 1
    return n, dsha(f"{prev}|{data}|{n}")

CH_DATA = ["Alice -> Bob  1 BTC", "Bob -> Carol  0.5 BTC", "Carol -> Dave  0.2 BTC"]
CH = []
prev = "0" * 64
for dt in CH_DATA:
    n, h = mine(prev, dt); CH.append((prev, dt, n, h)); prev = h
TAMPER = "Bob -> Carol  50 BTC"
TAMPER_H = dsha(f"{CH[1][0]}|{TAMPER}|{CH[1][2]}")
assert not TAMPER_H.startswith("00")

# ------------------------------------------------------------------ scenes
def s_title(d, t):
    a = fade(t, 0.1)
    cx, cy = 640, 215
    d.ellipse((cx - 70, cy - 70, cx + 70, cy + 70), fill=mix(ORANGE, a))
    T(d, cx, cy, "B", KRB(96), BG, a, "mm")
    d.rectangle((cx - 12, cy - 88, cx - 6, cy - 70), fill=mix(ORANGE, a))
    d.rectangle((cx + 8, cy - 88, cx + 14, cy - 70), fill=mix(ORANGE, a))
    d.rectangle((cx - 12, cy + 70, cx - 6, cy + 88), fill=mix(ORANGE, a))
    d.rectangle((cx + 8, cy + 70, cx + 14, cy + 88), fill=mix(ORANGE, a))
    T(d, 640, 350, "비트코인 해시는 어떻게 작동할까?", KRB(54), FG, fade(t, 0.6), "mm")
    T(d, 640, 430, "SHA-256  ·  블록 헤더  ·  채굴  ·  블록체인", KR(28), DIM, fade(t, 1.4), "mm")

def hash_io(d, y, text, h, t, t_type, t_hash, diff=None, a=1.0):
    R(d, (60, y, 390, y + 120), PANEL, LINE, a)
    T(d, 76, y + 8, "입력", KR(16), DIM, a)
    n = int(max(0, min(1, (t - t_type) / 1.6)) * len(text))
    cur = "_" if int(t * 3) % 2 == 0 and n < len(text) else ""
    T(d, 76, y + 50, text[:n] + cur, MONO(30), FG, a)
    arrow(d, 405, 490, y + 60, ORANGE, a)
    T(d, 447, y + 38, "SHA-256", KRB(18), ORANGE, a, "mm")
    if t >= t_hash:
        s = scramble(h, t_hash, t)
        done = t >= t_hash + 64 * 0.04
        f = MONO(28)
        for line in range(2):
            seg = s[line * 32:(line + 1) * 32]
            cols = None
            if diff is not None and done and diff["on"]:
                cols = [RED if diff["ref"][line * 32 + i] != seg[i] else FG for i in range(32)]
            hash_row(d, 510, y + 16 + line * 48, seg, f, cols, a)
        T(d, 510, y - 8, "출력 (256비트 = 64자리 16진수)", KR(16), DIM, a)

def s_hash(d, t):
    T(d, 60, 40, "해시 함수: SHA-256", KRB(40), FG)
    hash_io(d, 150, "Hello Bitcoin", H1, t, 0.6, 2.8)
    if t >= 6.5:
        a = fade(t, 6.5)
        hash_io(d, 340, "Hello bitcoin", H2, t, 7.0, 9.0,
                {"on": t >= 11.2, "ref": H1}, a)
    if t >= 11.2:
        a = fade(t, 11.2)
        T(d, 60, 500, f"256비트 중 {DIFF_BITS}개가 달라짐 (약 {DIFF_BITS * 100 // 256}%)  ·  빨간 글자 = 첫 번째 해시와 다른 자리",
          KRB(26), RED, a)
        T(d, 60, 548, "눈사태 효과(Avalanche effect): 입력이 조금만 달라도 결과는 예측 불가능하게 변한다",
          KR(22), DIM, a)

def s_props(d, t):
    T(d, 60, 40, "좋은 해시 함수의 3가지 성질", KRB(40), FG)
    ex = [sha("Hello")[:12], sha("hello")[:12]]
    cards = [
        ("1", "결정적", "같은 입력이면\n언제나 같은 해시", [("Hello", ex[0], FG), ("Hello", ex[0], FG)]),
        ("2", "단방향", "해시로부터 원래\n입력을 알아낼 수 없음", [(ex[0] + "…", "???", RED)]),
        ("3", "눈사태 효과", "입력이 조금만 달라도\n전혀 다른 해시", [("Hello", ex[0], FG), ("hello", ex[1], ORANGE)]),
    ]
    for i, (num, title, desc, exs) in enumerate(cards):
        a = fade(t, 0.5 + i * 2.6)
        x = 60 + i * 400
        R(d, (x, 150, x + 360, 500), PANEL, LINE, a, 18)
        d.ellipse((x + 24, 172, x + 72, 220), fill=mix(ORANGE, a))
        T(d, x + 48, 196, num, KRB(28), BG, a, "mm")
        T(d, x + 90, 178, title, KRB(32), FG, a)
        for k, ln in enumerate(desc.split("\n")):
            T(d, x + 28, 250 + k * 34, ln, KR(24), DIM, a)
        for k, (inp, outp, col) in enumerate(exs):
            y = 350 + k * 60
            T(d, x + 28, y, inp, MONO(24), FG, a)
            T(d, x + 28 + 120, y, "->", MONO(24), DIM, a)
            T(d, x + 28 + 165, y, outp, MONO(24), col, a)

def s_header(d, t):
    T(d, 60, 40, "비트코인의 블록 헤더 -> 블록 해시", KRB(40), FG)
    rows = [("버전", "0x20000000"), ("이전 블록 해시", "00000000a3f19c…"),
            ("머클 루트 (거래 요약)", "7d3c91be…"), ("타임스탬프", "1762939800"),
            ("난이도 목표 (bits)", "0x1d00ffff"), ("논스 (nonce)", "")]
    for i, (k, v) in enumerate(rows):
        a = fade(t, 0.4 + i * 0.6, 0.4)
        y = 130 + i * 68
        nonce = i == 5
        R(d, (60, y, 640, y + 56), PANEL, ORANGE if nonce else LINE, a, 10, 3 if nonce else 2)
        T(d, 78, y + 28, k, KR(22), ORANGE if nonce else DIM, a, "lm")
        if nonce:
            v = str(random.Random(int(t * 15)).randint(0, 4294967295)) if t > 5.5 else "?"
        T(d, 620, y + 28, v, MONO(24), ORANGE if nonce else FG, a, "rm")
    if t > 4.3:
        a = fade(t, 4.3)
        arrow(d, 660, 740, 330, DIM, a)
        R(d, (750, 270, 1010, 390), PANEL, ORANGE, a, 16, 3)
        T(d, 880, 315, "SHA-256", KRB(30), ORANGE, a, "mm")
        T(d, 880, 355, "x 2 (이중 해시)", KR(20), DIM, a, "mm")
        arrow(d, 1020, 1040, 330, DIM, a)
    if t > 5.5:
        a = fade(t, 5.5)
        h = scramble(dsha(BASE + "0"), 5.6, t, 0.03)
        T(d, 760, 430, "블록 해시", KRB(22), FG, a)
        for line in range(2):
            hash_row(d, 760, 470 + line * 36, h[line * 32:(line + 1) * 32], MONO(20), None, a)
    if t > 7.5:
        a = fade(t, 7.5)
        T(d, 660, 560, "논스: 채굴자가 값을 바꿔가며 시도하는 숫자", KRB(24), ORANGE, a)
        T(d, 660, 596, "(실제로는 타임스탬프·머클 루트도 함께 조정)", KR(18), DIM, a)

def s_mine(d, t):
    T(d, 60, 40, "채굴 = 조건에 맞는 해시 찾기", KRB(40), FG)
    found = t >= 11.0
    p = min(1.0, t / 11.0)
    idx = FOUND if found else int(FOUND * (p ** 2.0))
    # target banner
    R(d, (560, 120, 1220, 176), PANEL, ORANGE, 1, 12, 3)
    T(d, 580, 148, "목표: 해시가 ", KR(24), FG, 1, "lm")
    T(d, 735, 148, "0000", MONO(30), ORANGE, 1, "lm")
    T(d, 810, 148, " 으로 시작할 것", KR(24), FG, 1, "lm")
    # left
    R(d, (60, 120, 520, 540), PANEL, LINE, 1, 16)
    T(d, 80, 135, "블록 헤더 (일부)", KRB(22), FG)
    for k, ln in enumerate(["v=0x20000000", "prev=00000000a3f19c", "merkle=7d3c91be", "time=1762939800", "bits=0x1d00ffff"]):
        T(d, 80, 180 + k * 30, ln, MONO(22), DIM)
    T(d, 80, 350, "nonce", KR(20), DIM)
    T(d, 80, 378, f"{idx:,}", MONO(54), GREEN if found else ORANGE)
    T(d, 80, 460, f"시도 횟수: {idx + 1:,}", KR(22), FG)
    # right: attempts
    R(d, (560, 190, 1220, 540), PANEL, LINE, 1, 16)
    f = MONO(22)
    adv = f.getlength("0")
    for r in range(9):
        n = idx - 8 + r
        if n < 0: continue
        h = dsha(BASE + str(n))
        y = 205 + r * 36
        last = r == 8
        ok = h.startswith("0000")
        z = len(h) - len(h.lstrip("0"))
        T(d, 580, y, f"{n:>7,}", f, GREEN if (ok and found) else DIM)
        for i, ch in enumerate(h[:40]):
            c = FG
            if i < z: c = GREEN if ok else ORANGE
            T(d, 580 + (9 + i) * adv, y, ch, f, c, 1.0 if last else 0.55)
        T(d, 580 + 49 * adv, y, "…", f, DIM, 0.6)
    if found:
        a = fade(t, 11.0, 0.3)
        T(d, 640, 585, f"논스 {FOUND:,} 에서 발견!  해시 = {FOUND_H[:20]}…", KRB(28), GREEN, a, "mm")
    if t > 13.2:
        a = fade(t, 13.2)
        T(d, 640, 630, "실제 비트코인은 앞에 0이 훨씬 더 많이 필요하고, 전 세계 채굴기가 초당 수백 EH(10^18) 이상 시도합니다",
          KR(20), DIM, a, "mm")

def s_chain(d, t):
    T(d, 60, 40, "해시로 이어진 블록체인", KRB(40), FG)
    tam = t >= 5.0
    ta = fade(t, 5.0, 0.6)
    for i, (prv, dt, n, h) in enumerate(CH):
        x = 60 + i * 400
        a = fade(t, 0.3 + i * 0.5)
        broken = tam and i == 1
        col = RED if broken else GREEN
        R(d, (x, 150, x + 360, 450), PANEL, mix(col, 1) if False else col, a, 16, 3)
        T(d, x + 20, 162, f"블록 #{i + 1}", KRB(26), FG, a)
        T(d, x + 20, 205, "이전 블록 해시", KR(16), DIM, a)
        T(d, x + 20, 228, prv[:18] + "…", MONO(20), FG, a)
        T(d, x + 20, 270, "거래 데이터", KR(16), DIM, a)
        data = TAMPER if broken else dt
        T(d, x + 20, 293, data, MONO(20), RED if broken else FG, a)
        T(d, x + 20, 335, f"논스 {n}", KR(18), DIM, a)
        T(d, x + 20, 370, "내 해시", KR(16), DIM, a)
        hh = TAMPER_H if broken else h
        T(d, x + 20, 393, hh[:18] + "…", MONO(20), RED if broken else GREEN, a)
        if broken:
            T(d, x + 20, 422, "00으로 시작하지 않음 -> 채굴 조건 깨짐", KR(15), RED, ta)
        if i < 2:
            lc = RED if (tam and i == 1) else DIM
            arrow(d, x + 362, x + 398, 300, lc, a)
    if tam:
        T(d, 640, 495, "블록 #2의 해시가 바뀌었으므로, 블록 #3이 기록해 둔 '이전 해시'와 더 이상 맞지 않음",
          KRB(22), RED, ta, "mm")
        T(d, 640, 535, "-> 위조하려면 블록 #2부터 이후 모든 블록을 전부 다시 채굴해야 한다", KR(22), FG, fade(t, 7.5), "mm")
    else:
        T(d, 640, 495, "모든 블록이 앞 블록의 해시를 품고 있어 쇠사슬처럼 연결됨", KR(22), DIM, fade(t, 2.2), "mm")

def s_outro(d, t):
    T(d, 640, 150, "정리", KRB(48), FG, fade(t, 0.1), "mm")
    lines = ["해시: 어떤 데이터든 고정 길이의 지문으로 바꾸는 단방향 함수",
             "채굴: 논스를 바꿔가며 '조건에 맞는 해시'를 찾는 작업 (작업증명)",
             "체인: 이전 블록 해시를 포함해 과거 기록 위조를 사실상 불가능하게 만듦"]
    for i, ln in enumerate(lines):
        T(d, 640, 260 + i * 80, ln, KR(28), ORANGE if i == 1 else FG, fade(t, 0.8 + i * 1.0), "mm")

SCENES = [
    (4.5, s_title, []),
    (13.0, s_hash, [(0.5, "어떤 데이터를 넣어도 SHA-256은 항상 64자리(256비트) 해시를 만듭니다"),
                    (6.3, "이번엔 대문자 B를 소문자 b로, 딱 한 글자만 바꿔 봅니다"),
                    (11.4, "한 글자 차이인데 해시는 완전히 다른 값이 됩니다")]),
    (9.5, s_props, [(0.5, "해시 함수가 갖춰야 할 세 가지 성질")]),
    (10.0, s_header, [(0.5, "블록 헤더의 정보들을 모아서"),
                      (4.4, "SHA-256을 두 번 돌리면 블록 해시가 나옵니다"),
                      (7.6, "채굴자가 바꿀 수 있는 값이 바로 논스(nonce)입니다")]),
    (16.5, s_mine, [(0.5, "조건: 블록 해시가 목표값 이하여야 합니다 (여기선 0000으로 시작)"),
                    (3.5, "역산이 불가능하니 논스를 바꿔가며 무작정 해시를 돌려봅니다"),
                    (11.3, "찾았다! 이것이 작업증명(Proof of Work)입니다")]),
    (12.5, s_chain, [(0.5, "각 블록은 앞 블록의 해시를 담고 있어 사슬처럼 이어집니다"),
                     (5.2, "과거 거래를 하나 조작하면 그 블록의 해시가 바뀌고"),
                     (8.5, "뒤 블록과의 연결이 끊어져 들통납니다")]),
    (5.5, s_outro, []),
]
TOTAL = sum(s[0] for s in SCENES)

def render(gt):
    global G
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    acc = 0.0
    for dur, fn, caps in SCENES:
        if gt < acc + dur or (dur, fn, caps) is SCENES[-1]:
            t = gt - acc
            G = min(1.0, t / 0.35, (dur - t) / 0.35 + 0.0)
            G = max(G, 0.0)
            fn(d, t)
            cap = ""
            for ts, tx in caps:
                if t >= ts: cap = tx
            if cap:
                G = 1.0 if t < dur - 0.35 else G
                R(d, (40, 640, W - 40, 696), (0, 0, 0), None, 0.55 * G, 12)
                T(d, W // 2, 668, cap, KR(26), FG, 1.0, "mm")
            return img
        acc += dur
    return img

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "preview":
        out = sys.argv[2]
        for gt in [float(x) for x in sys.argv[3:]]:
            render(gt).save(os.path.join(out, f"f_{gt:05.1f}.png"))
        sys.exit()
    out = sys.argv[1]
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                           "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium", out],
                          stdin=subprocess.PIPE)
    n = int(TOTAL * FPS)
    for i in range(n):
        ff.stdin.write(render(i / FPS).tobytes())
    ff.stdin.close(); ff.wait()
    print("frames", n, "sec", TOTAL)
