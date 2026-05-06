#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
In-Fusion クローニング用プライマー設計ツール
"""

def read_sequence(filepath):
    """
    ファイルから塩基配列を読み込み、改行や空白を除去し、大文字に変換して返す。
    
    Args:
        filepath (str): 塩基配列ファイルのパス
    
    Returns:
        str: クリーンな大文字の塩基配列
    """
    with open(filepath, 'r') as f:
        sequence = f.read()
    # 改行と空白を除去し、大文字に変換
    sequence = ''.join(sequence.split()).upper()
    return sequence


def get_reverse_complement(sequence):
    """
    DNAシーケンスの逆相補鎖を返す。
    
    Args:
        sequence (str): DNAシーケンス
    
    Returns:
        str: 逆相補鎖
    """
    complement_map = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}
    # 相補鎖を作成して、反転させる
    complement = ''.join(complement_map[base] for base in sequence)
    reverse_complement = complement[::-1]
    return reverse_complement


def find_enzyme_site(vector_seq, enzyme_site):
    """
    ベクター塩基配列から制限酵素サイトを検索する。
    
    Args:
        vector_seq (str): ベクター塩基配列
        enzyme_site (str): 制限酵素サイト (e.g., "AGATCT")
    
    Returns:
        int: サイトのインデックス
    
    Raises:
        ValueError: 制限酵素サイトが見つからない場合
    """
    site_index = vector_seq.find(enzyme_site)
    if site_index == -1:
        raise ValueError(f"制限酵素サイト {enzyme_site} が見つかりません")
    return site_index


def linearize_vector(vector_seq, enzyme_site):
    """
    ベクターから制限酵素サイトを検索し、直鎖化する。
    BglII (AGATCT) の場合、A と G の間で切断される。
    戻り値の5'末端は "GATCT"、3'末端は "A" となるように再結合する。
    
    Args:
        vector_seq (str): ベクター塩基配列
        enzyme_site (str): 制限酵素サイト (e.g., "AGATCT")
    
    Returns:
        str: 直鎖化ベクター
    """
    site_index = find_enzyme_site(vector_seq, enzyme_site)
    
    # BglII は AGATCT で、A|GATCT の位置で切れる
    # サイト開始位置の直後（GATCTの前）で切れるので、
    # 5'末端 GATCT, 3'末端 A となる
    # 環状を直鎖化: サイトの直後から環を開く
    cut_position = site_index + 1  # A の直後が切断位置
    
    # 環状プラスミドを直線化
    linearized = vector_seq[cut_position:] + vector_seq[:cut_position]
    
    return linearized


def extract_homology_arms(linearized_vector, arm_length=15):
    """
    直鎖化ベクターの5'・3'末端から指定長の相同アームを抽出する。
    
    Args:
        linearized_vector (str): 直鎖化ベクター
        arm_length (int): 相同アームの長さ (デフォルト: 15 bp)
    
    Returns:
        tuple: (5'末端相同アーム, 3'末端相同アーム)
    """
    arm_5prime = linearized_vector[:arm_length]
    arm_3prime = linearized_vector[-arm_length:]
    
    return arm_5prime, arm_3prime


def calculate_tm(sequence):
    """
    簡易計算式 (Tm = 4*(G+C) + 2*(A+T)) を用いてTm値を計算する。
    
    Args:
        sequence (str): DNAシーケンス
    
    Returns:
        float: Tm値 (℃)
    """
    g_count = sequence.count('G')
    c_count = sequence.count('C')
    a_count = sequence.count('A')
    t_count = sequence.count('T')
    
    tm = 4 * (g_count + c_count) + 2 * (a_count + t_count)
    return tm


def check_consecutive_bases(sequence):
    """
    4塩基以上の連続した同一塩基を検出する。
    
    例：AAAA, GGGG などが含まれる場合を検出。
    
    Args:
        sequence (str): 塩基配列
    
    Returns:
        int: 検出された連続塩基の最大長（4以上）。検出されない場合は0。
    """
    max_consecutive = 0
    current_consecutive = 1
    
    for i in range(len(sequence) - 1):
        if sequence[i] == sequence[i + 1]:
            current_consecutive += 1
            max_consecutive = max(max_consecutive, current_consecutive)
        else:
            current_consecutive = 1
    
    return max(max_consecutive, 0)


def check_hairpin(sequence):
    """
    プライマー内部に3塩基以上の自己相補配列が存在するかチェックする。
    
    ヘアピン構造が形成される可能性を判定。
    
    注意: 左側領域と右側領域を独立して評価し、文字列結合による偽陽性を回避。
    
    Args:
        sequence (str): 塩基配列
    
    Returns:
        bool: ヘアピン形成の可能性がある場合は True
    """
    complement_map = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}
    
    # 3塩基以上の部分配列をチェック
    for length in range(3, len(sequence) // 2 + 1):
        for start in range(len(sequence) - length + 1):
            subseq = sequence[start:start + length]
            
            # 逆相補配列を計算
            complement = ''.join(complement_map[base] for base in subseq)
            reverse_complement = complement[::-1]
            
            # 左側領域と右側領域を独立して評価
            left_part = sequence[:start]
            right_part = sequence[start + length:]
            
            # いずれかの領域に逆相補配列が含まれるかチェック
            if reverse_complement in left_part or reverse_complement in right_part:
                return True
    
    return False


def is_valid_primer(sequence, is_forward=True):
    """
    プライマーが条件を満たすかチェックする。
    
    条件:
    1. 長さが 18 〜 25 bp であること。
    2. 3'末端が G または C であること（GCクランプ）。
       - Forward（通常向き）：sequence[-1] が G or C か判定
       - Reverse（逆相補鎖）：sequence[0] が G or C か判定
    3. GC含有率が 40 〜 60% であること。
    4. Tm値が 55 〜 65℃ であること。
    
    Args:
        sequence (str): 塩基配列
        is_forward (bool): Forward (True) or Reverse (False) のプライマー種別
    
    Returns:
        bool: 条件を満たす場合は True
    """
    # 条件1: 長さが 18 〜 25 bp
    if len(sequence) < 18 or len(sequence) > 25:
        return False
    
    # 条件2: 3'末端が G または C（GCクランプ）
    # Forward：3'末端 = sequence[-1]（末尾）
    # Reverse：3'末端 = 逆相補化後の末尾 = 元の配列の5'端 = sequence[0]
    if is_forward:
        if sequence[-1] not in ['G', 'C']:
            return False
    else:
        if sequence[0] not in ['G', 'C']:
            return False
    
    # 条件3: GC含有率が 40 〜 60%
    gc_count = sequence.count('G') + sequence.count('C')
    gc_content = gc_count / len(sequence) * 100
    if gc_content < 40 or gc_content > 60:
        return False
    
    # 条件4: Tm値が 55 〜 65℃
    tm = calculate_tm(sequence)
    if tm < 55 or tm > 65:
        return False
    
    return True


def calculate_penalty_score(sequence, is_forward=True):
    """
    プライマー条件からの外れ度を計算する（ペナルティスコア）。
    スコアが低いほど条件に近い。
    
    ペナルティ対象:
    1. GC含有率（目標: 40～60%）
    2. Tm値（目標: 55～65℃）
    3. 長さ（目標: 18～25 bp）
    4. GCクランプ不足（Forward: 3'末端, Reverse: 5'末端が G or C でない場合）
    5. 連続塩基（4塩基以上の連続した同一塩基）
    6. ヘアピン構造（3塩基以上の自己相補配列）
    
    Args:
        sequence (str): 塩基配列
        is_forward (bool): Forward (True) or Reverse (False) のプライマー種別
    
    Returns:
        float: ペナルティスコア
    """
    penalty = 0.0
    
    # GC含有率の評価（目標: 40～60%）
    gc_count = sequence.count('G') + sequence.count('C')
    gc_content = gc_count / len(sequence) * 100
    if gc_content < 40:
        penalty += (40 - gc_content) ** 2 / 100
    elif gc_content > 60:
        penalty += (gc_content - 60) ** 2 / 100
    
    # Tm値の評価（目標: 55～65℃）
    tm = calculate_tm(sequence)
    if tm < 55:
        penalty += (55 - tm) ** 2 / 100
    elif tm > 65:
        penalty += (tm - 65) ** 2 / 100
    
    # 長さの評価（目標: 18～25 bp）
    if len(sequence) < 18:
        penalty += (18 - len(sequence)) ** 2
    elif len(sequence) > 25:
        penalty += (len(sequence) - 25) ** 2
    
    # GCクランプの評価
    if is_forward:
        # Forward: 3'末端（sequence[-1]）が G or C か判定
        if sequence[-1] not in ['G', 'C']:
            penalty += 5.0
    else:
        # Reverse: 5'末端（sequence[0]）が G or C か判定
        if sequence[0] not in ['G', 'C']:
            penalty += 5.0
    
    # 連続塩基の回避（4塩基以上の連続した同一塩基）
    consecutive = check_consecutive_bases(sequence)
    if consecutive >= 4:
        penalty += (consecutive - 3) * 10
    
    # ヘアピン構造の回避（3塩基以上の自己相補配列）
    if check_hairpin(sequence):
        penalty += 20.0
    
    return penalty


def find_forward_primer(insert_seq):
    """
    インサートの最初の塩基（index 0）から開始する特異的プライマー配列を探索する。
    
    探索ルール:
    - Forward用は insert_seq[0:length] で抽出（最初の位置で固定）
    - length は 18 から 25 bp の範囲で探索
    - 条件を満たす最初の配列を返す
    - 見つからない場合は、ペナルティスコアが最小の配列を返す
    
    Args:
        insert_seq (str): インサート塩基配列
    
    Returns:
        str: Forward用特異的配列、見つからない場合はフォールバック
    """
    best_candidate = None
    best_penalty = float('inf')
    
    for length in range(18, 26):
        if length > len(insert_seq):
            continue
        
        candidate = insert_seq[0:length]
        
        # 条件を満たすかチェック（Forward用）
        if is_valid_primer(candidate, is_forward=True):
            return candidate
        
        # ペナルティスコアを計算してフォールバック候補を保存
        penalty = calculate_penalty_score(candidate, is_forward=True)
        if penalty < best_penalty:
            best_penalty = penalty
            best_candidate = candidate
    
    # 条件を満たす配列が見つからない場合のフォールバック
    if best_candidate is None:
        # 長さ 20 bp をデフォルトとして返す
        if len(insert_seq) >= 20:
            return insert_seq[0:20]
        else:
            return insert_seq
    
    return best_candidate


def find_reverse_primer(insert_seq):
    """
    インサートの最後の塩基（末尾）で終わる特異的プライマー配列を探索する。
    
    探索ルール:
    - Reverse用は insert_seq[-length:] で抽出（最後の位置で固定）
    - length は 18 から 25 bp の範囲で探索（短いものから長いものへ）
    - 条件を満たす最初の配列を返す
    - 見つからない場合は、ペナルティスコアが最小の配列を返す
    
    Args:
        insert_seq (str): インサート塩基配列
    
    Returns:
        str: Reverse用特異的配列（元の向き）、見つからない場合はフォールバック
    """
    best_candidate = None
    best_penalty = float('inf')
    
    for length in range(18, 26):
        if length > len(insert_seq):
            continue
        
        candidate = insert_seq[-length:]
        
        # 条件を満たすかチェック（Reverse用）
        if is_valid_primer(candidate, is_forward=False):
            return candidate
        
        # ペナルティスコアを計算してフォールバック候補を保存
        penalty = calculate_penalty_score(candidate, is_forward=False)
        if penalty < best_penalty:
            best_penalty = penalty
            best_candidate = candidate
    
    # 条件を満たす配列が見つからない場合のフォールバック
    if best_candidate is None:
        # 長さ 20 bp をデフォルトとして返す
        if len(insert_seq) >= 20:
            return insert_seq[-20:]
        else:
            return insert_seq
    
    return best_candidate


def design_gene_specific_primers(insert_seq):
    """
    インサートの両端から「特異的配列」を探索する。
    
    探索条件（優先順位順）:
    1. 長さが 18 〜 25 bp であること。
    2. 3'末端が G または C であること（GCクランプ）。
       - Forward：3'末端（末尾）が G or C
       - Reverse：3'末端の元の配列における5'端（最初）が G or C
    3. GC含有率が 40 〜 60% であること。
    4. Tm値が 55 〜 65℃ であること。
    5. 連続塩基や二次構造の回避。
    
    注意: ForwardとReverseのTm値の差が 5℃ を超える場合、警告を出力。
    
    Args:
        insert_seq (str): インサート塩基配列
    
    Returns:
        tuple: (Forward用特異的配列, Reverse用特異的配列（元の向き）)
    """
    forward_seq = find_forward_primer(insert_seq)
    reverse_seq = find_reverse_primer(insert_seq)
    
    # Tm値バランスの確認
    forward_tm = calculate_tm(forward_seq)
    reverse_tm = calculate_tm(reverse_seq)
    tm_diff = abs(forward_tm - reverse_tm)
    
    if tm_diff > 5:
        import sys
        warning_msg = (
            f"【 警告 】Tm値のバランスが大きく異なります。\n"
            f"  Forward Tm: {forward_tm:.1f}℃\n"
            f"  Reverse Tm: {reverse_tm:.1f}℃\n"
            f"  差分: {tm_diff:.1f}℃ (推奨: 5℃以下)\n"
            f"  PCR効率の低下につながる可能性があります。"
        )
        print(warning_msg, file=sys.stderr)
    
    return forward_seq, reverse_seq


def trim_forward_overlap(arm_3prime, forward_specific):
    """
    Forward側の結合境界で1塩基の重複がある場合に、特異的配列側を1塩基短縮する。

    Args:
        arm_3prime (str): ベクターの上流側相同アーム
        forward_specific (str): Forward用特異的配列

    Returns:
        str: 重複を除去したForward用特異的配列
    """
    if arm_3prime and forward_specific and arm_3prime[-1] == forward_specific[0]:
        return forward_specific[1:]
    return forward_specific


def trim_reverse_overlap(arm_5prime, reverse_specific):
    """
    Reverse側の結合境界で1塩基の重複がある場合に、元の向きの特異的配列側を1塩基短縮する。

    Args:
        arm_5prime (str): ベクターの切断部位下流側相同アーム
        reverse_specific (str): Reverse用特異的配列（元の向き）

    Returns:
        str: 重複を除去したReverse用特異的配列（元の向き）
    """
    if arm_5prime and reverse_specific and arm_5prime[0] == reverse_specific[-1]:
        return reverse_specific[:-1]
    return reverse_specific


def generate_infusion_primers(homology_arms, specific_seqs):
    """
    Forward/Reverse プライマーを生成する。
    - Forward: [3'側相同アーム] + [Forward用特異的配列]
    - Reverse: [5'側相同アームの逆相補鎖] + [Reverse用特異的配列の逆相補鎖]

    結合境界で1塩基が重複する場合は、重複分を除去してから結合する。
    
    Args:
        homology_arms (tuple): (5'末端相同アーム, 3'末端相同アーム)
        specific_seqs (tuple): (Forward用特異的配列, Reverse用特異的配列)
    
    Returns:
        tuple: (Forwardプライマー, Reverseプライマー)
    """
    arm_5prime, arm_3prime = homology_arms
    forward_specific, reverse_specific = specific_seqs
    
    # Forward プライマー: 3'相同アーム + Forward特異的配列
    trimmed_forward_specific = trim_forward_overlap(arm_3prime, forward_specific)
    forward_primer = arm_3prime + trimmed_forward_specific
    
    # Reverse プライマー: 5'相同アームの逆相補鎖 + Reverse特異的配列の逆相補鎖
    trimmed_reverse_specific = trim_reverse_overlap(arm_5prime, reverse_specific)
    arm_5prime_rc = get_reverse_complement(arm_5prime)
    reverse_specific_rc = get_reverse_complement(trimmed_reverse_specific)
    reverse_primer = arm_5prime_rc + reverse_specific_rc
    
    return forward_primer, reverse_primer

