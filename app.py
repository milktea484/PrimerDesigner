#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
In-Fusion クローニング用プライマー設計ツール - 統合エントリーポイント
CUI（自動化用）と GUI（手動操作用）の両方をサポート。

使用方法:
  - GUI モード: python app.py
  - CUI モード: python app.py --vector <path> --insert <path> --enzyme <path> [--output <path>] [--json]
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any

# PyQt6 imports
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QFileDialog, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt

# Core library imports
from src.primer_designer import (
    read_sequence,
    linearize_vector,
    extract_homology_arms,
    design_gene_specific_primers,
    generate_infusion_primers,
    calculate_tm,
    get_reverse_complement
)


class PrimerDesignLogic:
    """プライマー設計のビジネスロジック（CUI/GUI共通）"""
    
    @staticmethod
    def run_pipeline(vector_file: str, insert_file: str, enzyme_file: str) -> Dict[str, Any]:
        """
        プライマー設計パイプラインを実行する。
        
        Args:
            vector_file (str): ベクターファイルパス
            insert_file (str): インサートファイルパス
            enzyme_file (str): 制限酵素サイトファイルパス
        
        Returns:
            dict: 設計結果を含む辞書
        
        Raises:
            FileNotFoundError: ファイルが見つからない場合
            ValueError: 制限酵素サイトが見つからない場合
        """
        # ステップ1: 塩基配列を読み込み
        vector_seq = read_sequence(vector_file)
        insert_seq = read_sequence(insert_file)
        enzyme_site = read_sequence(enzyme_file)
        
        # ステップ2: ベクターを直鎖化
        linearized_vector = linearize_vector(vector_seq, enzyme_site)
        
        # ステップ3: 相同アームを抽出
        arm_5prime, arm_3prime = extract_homology_arms(linearized_vector, arm_length=15)
        
        # ステップ4: 特異的プライマーを設計
        forward_specific, reverse_specific = design_gene_specific_primers(insert_seq)
        
        # ステップ5: 最終プライマーを生成
        forward_primer, reverse_primer = generate_infusion_primers(
            (arm_5prime, arm_3prime),
            (forward_specific, reverse_specific)
        )
        
        # 計算結果をまとめる
        result = {
            "vector_length": len(linearized_vector),
            "insert_length": len(insert_seq),
            "enzyme_site": enzyme_site,
            "homology_arm_5prime": arm_5prime,
            "homology_arm_3prime": arm_3prime,
            "forward_specific": forward_specific,
            "forward_specific_length": len(forward_specific),
            "forward_specific_tm": calculate_tm(forward_specific),
            "forward_specific_gc": (forward_specific.count('G') + forward_specific.count('C')) / len(forward_specific) * 100,
            "forward_primer": forward_primer,
            "forward_primer_length": len(forward_primer),
            "reverse_specific": reverse_specific,
            "reverse_specific_length": len(reverse_specific),
            "reverse_specific_tm": calculate_tm(reverse_specific),
            "reverse_specific_gc": (reverse_specific.count('G') + reverse_specific.count('C')) / len(reverse_specific) * 100,
            "reverse_primer": reverse_primer,
            "reverse_primer_length": len(reverse_primer),
        }
        
        return result
    
    @staticmethod
    def format_result_text(result: Dict[str, Any]) -> str:
        """
        設計結果をテキスト形式でフォーマットする。
        
        Args:
            result (dict): 設計結果
        
        Returns:
            str: フォーマットされたテキスト
        """
        tm_diff = abs(result["forward_specific_tm"] - result["reverse_specific_tm"])
        warning = ""
        if tm_diff > 5:
            warning = f"\n【 警告 】Tm値のバランスが大きく異なります。\n  差分: {tm_diff:.1f}℃ (推奨: 5℃以下)"
        
        text = f"""
============================================================
【 プライマー設計結果 】
============================================================

【ベクター・インサート情報】
  直鎖化ベクター長: {result['vector_length']} bp
  インサート長: {result['insert_length']} bp
  制限酵素サイト: {result['enzyme_site']}

【相同アーム】
  5'末端相同アーム (15 bp): {result['homology_arm_5prime']}
  3'末端相同アーム (15 bp): {result['homology_arm_3prime']}

【Forwardプライマー】
  特異的配列: {result['forward_specific']}
    - 長さ: {result['forward_specific_length']} bp
    - Tm値: {result['forward_specific_tm']:.1f}℃
    - GC含有率: {result['forward_specific_gc']:.1f}%
  
  最終プライマー: {result['forward_primer']}
    - 長さ: {result['forward_primer_length']} bp

【Reverseプライマー】
  特異的配列: {result['reverse_specific']}
    - 長さ: {result['reverse_specific_length']} bp
    - Tm値: {result['reverse_specific_tm']:.1f}℃
    - GC含有率: {result['reverse_specific_gc']:.1f}%
  
  最終プライマー: {result['reverse_primer']}
    - 長さ: {result['reverse_primer_length']} bp

【Tm値バランス】
  Forward Tm: {result['forward_specific_tm']:.1f}℃
  Reverse Tm: {result['reverse_specific_tm']:.1f}℃
  差分: {tm_diff:.1f}℃{warning}

============================================================
✓ プライマー設計完了
============================================================
"""
        return text


class PrimerDesignGUI(QMainWindow):
    """GUI用のメインウィンドウ"""
    
    def __init__(self):
        super().__init__()
        self.vector_file = ""
        self.insert_file = ""
        self.enzyme_file = ""
        
        self.init_ui()
    
    def init_ui(self):
        """UI初期化"""
        self.setWindowTitle("In-Fusion プライマー設計ツール")
        self.setGeometry(100, 100, 900, 800)
        
        # メインウィジェット
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # レイアウト
        layout = QVBoxLayout()
        
        # ベクターファイル選択
        vector_layout = QHBoxLayout()
        vector_layout.addWidget(QLabel("ベクターファイル:"))
        self.vector_input = QLineEdit()
        self.vector_input.setReadOnly(True)
        vector_layout.addWidget(self.vector_input)
        vector_btn = QPushButton("参照")
        vector_btn.clicked.connect(self.select_vector_file)
        vector_layout.addWidget(vector_btn)
        layout.addLayout(vector_layout)
        
        # インサートファイル選択
        insert_layout = QHBoxLayout()
        insert_layout.addWidget(QLabel("インサートファイル:"))
        self.insert_input = QLineEdit()
        self.insert_input.setReadOnly(True)
        insert_layout.addWidget(self.insert_input)
        insert_btn = QPushButton("参照")
        insert_btn.clicked.connect(self.select_insert_file)
        insert_layout.addWidget(insert_btn)
        layout.addLayout(insert_layout)
        
        # 制限酵素ファイル選択
        enzyme_layout = QHBoxLayout()
        enzyme_layout.addWidget(QLabel("制限酵素ファイル:"))
        self.enzyme_input = QLineEdit()
        self.enzyme_input.setReadOnly(True)
        enzyme_layout.addWidget(self.enzyme_input)
        enzyme_btn = QPushButton("参照")
        enzyme_btn.clicked.connect(self.select_enzyme_file)
        enzyme_layout.addWidget(enzyme_btn)
        layout.addLayout(enzyme_layout)
        
        # 実行ボタン
        run_btn = QPushButton("プライマー設計を実行")
        run_btn.clicked.connect(self.run_design)
        layout.addWidget(run_btn)
        
        # 結果表示エリア
        layout.addWidget(QLabel("実行結果:"))
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)
        
        main_widget.setLayout(layout)
    
    def select_vector_file(self):
        """ベクターファイルを選択"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "ベクターファイルを選択", "", "DNA Files (*.dna *.seq);;All Files (*)"
        )
        if file_path:
            self.vector_file = file_path
            self.vector_input.setText(file_path)
    
    def select_insert_file(self):
        """インサートファイルを選択"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "インサートファイルを選択", "", "DNA Files (*.dna *.seq);;All Files (*)"
        )
        if file_path:
            self.insert_file = file_path
            self.insert_input.setText(file_path)
    
    def select_enzyme_file(self):
        """制限酵素ファイルを選択"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "制限酵素ファイルを選択", "", "DNA Files (*.dna *.seq);;All Files (*)"
        )
        if file_path:
            self.enzyme_file = file_path
            self.enzyme_input.setText(file_path)
    
    def run_design(self):
        """プライマー設計を実行"""
        # ファイルが選択されているか確認
        if not self.vector_file or not self.insert_file or not self.enzyme_file:
            QMessageBox.warning(self, "エラー", "すべてのファイルを選択してください。")
            return
        
        try:
            # ビジネスロジックを実行
            result = PrimerDesignLogic.run_pipeline(
                self.vector_file,
                self.insert_file,
                self.enzyme_file
            )
            
            # 結果をテキスト形式でフォーマット
            output_text = PrimerDesignLogic.format_result_text(result)
            self.result_text.setText(output_text)
        
        except FileNotFoundError as e:
            error_msg = f"ファイルが見つかりません:\n{e}"
            QMessageBox.critical(self, "エラー", error_msg)
            self.result_text.setText(error_msg)
        
        except ValueError as e:
            error_msg = f"エラー:\n{e}"
            QMessageBox.critical(self, "エラー", error_msg)
            self.result_text.setText(error_msg)
        
        except Exception as e:
            error_msg = f"予期しないエラーが発生しました:\n{e}"
            QMessageBox.critical(self, "エラー", error_msg)
            self.result_text.setText(error_msg)


def run_cui(args):
    """CUIモード（自動化用）を実行"""
    try:
        # パイプラインを実行
        result = PrimerDesignLogic.run_pipeline(
            args.vector,
            args.insert,
            args.enzyme
        )
        
        if args.json:
            # JSON形式で出力
            output = json.dumps(result, ensure_ascii=False, indent=2)
        else:
            # テキスト形式で出力
            output = PrimerDesignLogic.format_result_text(result)
        
        # 出力先を決定
        if args.output:
            output_file = Path(args.output)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"結果を {output_file} に保存しました。")
        else:
            print(output)
    
    except FileNotFoundError as e:
        print(f"エラー: ファイルが見つかりません: {e}", file=sys.stderr)
        sys.exit(1)
    
    except ValueError as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)
    
    except Exception as e:
        print(f"予期しないエラーが発生しました: {e}", file=sys.stderr)
        sys.exit(1)


def run_gui():
    """GUIモード（手動操作用）を実行"""
    app = QApplication(sys.argv)
    window = PrimerDesignGUI()
    window.show()
    sys.exit(app.exec())


def main():
    """メインエントリーポイント"""
    # sys.argv の長さで起動モードを判定
    if len(sys.argv) > 1:
        # CUIモード
        parser = argparse.ArgumentParser(
            description="In-Fusion クローニング用プライマー設計ツール"
        )
        parser.add_argument(
            "--vector",
            required=True,
            help="ベクターファイルのパス"
        )
        parser.add_argument(
            "--insert",
            required=True,
            help="インサートファイルのパス"
        )
        parser.add_argument(
            "--enzyme",
            required=True,
            help="制限酵素サイトファイルのパス"
        )
        parser.add_argument(
            "--output",
            help="出力ファイルのパス（指定なしの場合は標準出力）"
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="JSON形式で出力"
        )
        
        args = parser.parse_args()
        run_cui(args)
    else:
        # GUIモード
        run_gui()


if __name__ == "__main__":
    main()
