#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
In-Fusion クローニング用プライマー設計ツール実行スクリプト
標準出力とログファイルの両方に結果を出力
"""

import sys
import logging
from datetime import datetime
from pathlib import Path

# srcディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from primer_designer import (
    read_sequence,
    linearize_vector,
    extract_homology_arms,
    calculate_tm,
    design_gene_specific_primers,
    generate_infusion_primers,
)


def setup_logging(log_dir='logs'):
    """
    ロギングを設定する。
    標準出力とログファイルの両方に出力される。
    
    Args:
        log_dir (str): ログファイルの出力先ディレクトリ
    
    Returns:
        logging.Logger: 設定されたロガー
    """
    log_path = Path(__file__).parent.parent / log_dir
    log_path.mkdir(exist_ok=True)
    
    # ログファイル名: 実行日時を含む
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_path / f'primer_design_{timestamp}.log'
    
    # ロガーの設定
    logger = logging.getLogger('PrimerDesigner')
    logger.setLevel(logging.INFO)
    
    # フォーマッタの設定
    formatter = logging.Formatter(
        fmt='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # ファイルハンドラー (ログファイルに出力)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # ストリームハンドラー (標準出力に出力)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    
    return logger


def main():
    """
    メイン処理: ファイルを読み込み、プライマーを設計し、結果を出力する。
    """
    # ロギング設定
    logger = setup_logging()
    
    # ファイルパスの定義
    base_dir = Path(__file__).parent.parent
    vector_file = base_dir / 'data' / 'plasmid' / 'p10A1.dna'
    insert_file = base_dir / 'data' / 'insert' / 'sample.dna'
    enzyme_file = base_dir / 'data' / 'restriction_digest' / 'BglII.seq'
    
    # Step 1: 塩基配列を読み込む
    logger.info("=" * 60)
    logger.info("In-Fusion クローニング用プライマー設計ツール")
    logger.info("=" * 60)
    logger.info("")
    logger.info("[ステップ1] 塩基配列を読み込み中...")
    
    try:
        vector_seq = read_sequence(str(vector_file))
        insert_seq = read_sequence(str(insert_file))
        enzyme_site = read_sequence(str(enzyme_file))
        
        logger.info(f"✓ ベクター長: {len(vector_seq)} bp")
        logger.info(f"✓ インサート長: {len(insert_seq)} bp")
        logger.info(f"✓ 制限酵素サイト: {enzyme_site}")
    except FileNotFoundError as e:
        logger.error(f"✗ ファイルが見つかりません: {e}")
        return 1
    
    # Step 2: ベクターを直鎖化
    logger.info("")
    logger.info("[ステップ2] ベクターを直鎖化中...")
    
    try:
        linearized_vector = linearize_vector(vector_seq, enzyme_site)
        logger.info(f"✓ 直鎖化ベクター長: {len(linearized_vector)} bp")
    except ValueError as e:
        logger.error(f"✗ エラー: {e}")
        return 1
    
    # Step 3: 相同アームを抽出
    logger.info("")
    logger.info("[ステップ3] 相同アームを抽出中...")
    arm_5prime, arm_3prime = extract_homology_arms(linearized_vector, arm_length=15)
    logger.info(f"✓ 5'末端相同アーム (15 bp): {arm_5prime}")
    logger.info(f"✓ 3'末端相同アーム (15 bp): {arm_3prime}")
    
    # Step 4: 特異的プライマーを設計
    logger.info("")
    logger.info("[ステップ4] 特異的プライマーを設計中...")
    forward_specific, reverse_specific = design_gene_specific_primers(insert_seq)
    
    if forward_specific:
        gc_f = (forward_specific.count('G') + forward_specific.count('C')) / len(forward_specific) * 100
        tm_f = calculate_tm(forward_specific)
        logger.info(f"✓ Forward特異的配列: {forward_specific}")
        logger.info(f"  - 長さ: {len(forward_specific)} bp")
        logger.info(f"  - GC含有率: {gc_f:.1f}%")
        logger.info(f"  - Tm値: {tm_f:.1f}℃")
    else:
        logger.warning("✗ Forward特異的配列が見つかりません")
    
    if reverse_specific:
        gc_r = (reverse_specific.count('G') + reverse_specific.count('C')) / len(reverse_specific) * 100
        tm_r = calculate_tm(reverse_specific)
        logger.info(f"✓ Reverse特異的配列: {reverse_specific}")
        logger.info(f"  - 長さ: {len(reverse_specific)} bp")
        logger.info(f"  - GC含有率: {gc_r:.1f}%")
        logger.info(f"  - Tm値: {tm_r:.1f}℃")
    else:
        logger.warning("✗ Reverse特異的配列が見つかりません")
    
    # Step 5: 最終プライマーを生成
    logger.info("")
    logger.info("[ステップ5] 最終プライマーを生成中...")
    
    if forward_specific and reverse_specific:
        forward_primer, reverse_primer = generate_infusion_primers(
            (arm_5prime, arm_3prime),
            (forward_specific, reverse_specific)
        )
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("【 最終結果 】")
        logger.info("=" * 60)
        logger.info("")
        
        logger.info(f"直鎖化ベクター長: {len(linearized_vector)} bp")
        logger.info("")
        
        tm_f = calculate_tm(forward_specific)
        logger.info(f"[Forwardプライマー]")
        logger.info(f"配列: {forward_primer}")
        logger.info(f"長さ: {len(forward_primer)} bp")
        logger.info(f"Tm値（特異的配列部分）: {tm_f:.1f}℃")
        logger.info("")
        
        tm_r = calculate_tm(reverse_specific)
        logger.info(f"[Reverseプライマー]")
        logger.info(f"配列: {reverse_primer}")
        logger.info(f"長さ: {len(reverse_primer)} bp")
        logger.info(f"Tm値（特異的配列部分）: {tm_r:.1f}℃")
        logger.info("")
        
        logger.info("=" * 60)
        logger.info("✓ プライマー設計完了")
        logger.info("=" * 60)
        
        return 0
    else:
        logger.error("✗ プライマー設計に失敗しました")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
