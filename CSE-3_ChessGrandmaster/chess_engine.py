"""
Infinite Chess Grandmaster - Generalized Chess Engine
Supports N×N boards with bombs, teleporters, and time dilation.
"""

import numpy as np
from enum import Enum
from typing import List, Tuple, Optional, Dict, Set
from dataclasses import dataclass, field
import time
import json
import random

class PieceType(Enum):
    EMPTY = 0
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6

class Color(Enum):
    WHITE = 0
    BLACK = 1

@dataclass
class Piece:
    piece_type: PieceType
    color: Color
    
    def __str__(self):
        symbols = {
            PieceType.EMPTY: '.',
            PieceType.PAWN: 'P' if self.color == Color.WHITE else 'p',
            PieceType.KNIGHT: 'N' if self.color == Color.WHITE else 'n',
            PieceType.BISHOP: 'B' if self.color == Color.WHITE else 'b',
            PieceType.ROOK: 'R' if self.color == Color.WHITE else 'r',
            PieceType.QUEEN: 'Q' if self.color == Color.WHITE else 'q',
            PieceType.KING: 'K' if self.color == Color.WHITE else 'k',
        }
        return symbols[self.piece_type]

@dataclass
class SpecialSquare:
    square_type: str  # 'bomb', 'teleporter_in', 'teleporter_out'
    position: Tuple[int, int]
    pair_position: Optional[Tuple[int, int]] = None  # For teleporters

@dataclass
class Move:
    from_pos: Tuple[int, int]
    to_pos: Tuple[int, int]
    promotion: Optional[PieceType] = None
    
    def __str__(self):
        return f"{self.from_pos}->{self.to_pos}"

class GameState:
    def __init__(self, board_size: int = 8):
        self.board_size = board_size
        self.board: List[List[Optional[Piece]]] = [[None] * board_size for _ in range(board_size)]
        self.current_player = Color.WHITE
        self.move_count = 0
        self.special_squares: List[SpecialSquare] = []
        self.time_dilation_counter = 0
        self.extra_move_available = False
        self.captured_pieces: Dict[Color, List[Piece]] = {Color.WHITE: [], Color.BLACK: []}
        self.move_history: List[Move] = []
        
    def initialize_standard(self):
        """Initialize standard chess position"""
        # Place pawns
        for col in range(self.board_size):
            self.board[1][col] = Piece(PieceType.PAWN, Color.WHITE)
            self.board[self.board_size - 2][col] = Piece(PieceType.PAWN, Color.BLACK)
        
        # Place major pieces (adapted for board size)
        back_rank = [
            PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN,
            PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK
        ]
        
        # For larger boards, add extra pieces
        if self.board_size > 8:
            extra_pieces = [PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP]
            back_rank = extra_pieces + back_rank + extra_pieces
        
        for col, piece_type in enumerate(back_rank[:self.board_size]):
            self.board[0][col] = Piece(piece_type, Color.WHITE)
            self.board[self.board_size - 1][col] = Piece(piece_type, Color.BLACK)
    
    def add_bombs(self, positions: List[Tuple[int, int]]):
        """Add bomb squares"""
        for pos in positions:
            self.special_squares.append(SpecialSquare('bomb', pos))
    
    def add_teleporters(self, pairs: List[Tuple[Tuple[int, int], Tuple[int, int]]]):
        """Add teleporter pairs"""
        for pos1, pos2 in pairs:
            self.special_squares.append(SpecialSquare('teleporter_in', pos1, pos2))
            self.special_squares.append(SpecialSquare('teleporter_out', pos2, pos1))
    
    def get_piece(self, pos: Tuple[int, int]) -> Optional[Piece]:
        row, col = pos
        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            return self.board[row][col]
        return None
    
    def is_valid_position(self, pos: Tuple[int, int]) -> bool:
        row, col = pos
        return 0 <= row < self.board_size and 0 <= col < self.board_size
    
    def get_pseudo_legal_moves(self, pos: Tuple[int, int]) -> List[Move]:
        """Get all pseudo-legal moves for piece at position"""
        piece = self.get_piece(pos)
        if not piece or piece.piece_type == PieceType.EMPTY:
            return []
        
        moves = []
        row, col = pos
        
        if piece.piece_type == PieceType.PAWN:
            moves.extend(self._get_pawn_moves(pos, piece.color))
        elif piece.piece_type == PieceType.KNIGHT:
            moves.extend(self._get_knight_moves(pos, piece.color))
        elif piece.piece_type == PieceType.BISHOP:
            moves.extend(self._get_bishop_moves(pos, piece.color))
        elif piece.piece_type == PieceType.ROOK:
            moves.extend(self._get_rook_moves(pos, piece.color))
        elif piece.piece_type == PieceType.QUEEN:
            moves.extend(self._get_queen_moves(pos, piece.color))
        elif piece.piece_type == PieceType.KING:
            moves.extend(self._get_king_moves(pos, piece.color))
        
        return moves
    
    def _get_pawn_moves(self, pos: Tuple[int, int], color: Color) -> List[Move]:
        moves = []
        row, col = pos
        direction = 1 if color == Color.WHITE else -1
        start_row = 1 if color == Color.WHITE else self.board_size - 2
        
        # Forward move
        new_row = row + direction
        if self.is_valid_position((new_row, col)) and not self.get_piece((new_row, col)):
            # Check for promotion
            promotion_row = self.board_size - 1 if color == Color.WHITE else 0
            if new_row == promotion_row:
                for promo in [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]:
                    moves.append(Move(pos, (new_row, col), promo))
            else:
                moves.append(Move(pos, (new_row, col)))
            
            # Double move from start
            if row == start_row:
                new_row2 = row + 2 * direction
                if self.is_valid_position((new_row2, col)) and not self.get_piece((new_row2, col)):
                    moves.append(Move(pos, (new_row2, col)))
        
        # Captures
        for dc in [-1, 1]:
            new_pos = (row + direction, col + dc)
            if self.is_valid_position(new_pos):
                target = self.get_piece(new_pos)
                if target and target.color != color:
                    if new_pos[0] == (self.board_size - 1 if color == Color.WHITE else 0):
                        for promo in [PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT]:
                            moves.append(Move(pos, new_pos, promo))
                    else:
                        moves.append(Move(pos, new_pos))
        
        return moves
    
    def _get_knight_moves(self, pos: Tuple[int, int], color: Color) -> List[Move]:
        moves = []
        row, col = pos
        offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        
        for dr, dc in offsets:
            new_pos = (row + dr, col + dc)
            if self.is_valid_position(new_pos):
                target = self.get_piece(new_pos)
                if not target or target.color != color:
                    moves.append(Move(pos, new_pos))
        
        return moves
    
    def _get_sliding_moves(self, pos: Tuple[int, int], color: Color, directions: List[Tuple[int, int]]) -> List[Move]:
        moves = []
        row, col = pos
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while self.is_valid_position((r, c)):
                target = self.get_piece((r, c))
                if not target:
                    moves.append(Move(pos, (r, c)))
                elif target.color != color:
                    moves.append(Move(pos, (r, c)))
                    break
                else:
                    break
                r, c = r + dr, c + dc
        
        return moves
    
    def _get_bishop_moves(self, pos: Tuple[int, int], color: Color) -> List[Move]:
        return self._get_sliding_moves(pos, color, [(-1, -1), (-1, 1), (1, -1), (1, 1)])
    
    def _get_rook_moves(self, pos: Tuple[int, int], color: Color) -> List[Move]:
        return self._get_sliding_moves(pos, color, [(-1, 0), (1, 0), (0, -1), (0, 1)])
    
    def _get_queen_moves(self, pos: Tuple[int, int], color: Color) -> List[Move]:
        return self._get_sliding_moves(pos, color, 
            [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)])
    
    def _get_king_moves(self, pos: Tuple[int, int], color: Color) -> List[Move]:
        moves = []
        row, col = pos
        
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_pos = (row + dr, col + dc)
                if self.is_valid_position(new_pos):
                    target = self.get_piece(new_pos)
                    if not target or target.color != color:
                        moves.append(Move(pos, new_pos))
        
        return moves
    
    def make_move(self, move: Move) -> bool:
        """Execute a move and update game state"""
        piece = self.get_piece(move.from_pos)
        if not piece:
            return False
        
        # Check for capture
        target = self.get_piece(move.to_pos)
        if target:
            self.captured_pieces[target.color].append(target)
        
        # Move piece
        self.board[move.to_pos[0]][move.to_pos[1]] = piece
        self.board[move.from_pos[0]][move.from_pos[1]] = None
        
        # Handle promotion
        if move.promotion:
            self.board[move.to_pos[0]][move.to_pos[1]] = Piece(move.promotion, piece.color)
        
        # Check for bomb
        for sq in self.special_squares:
            if sq.square_type == 'bomb' and sq.position == move.to_pos:
                self.board[move.to_pos[0]][move.to_pos[1]] = None
                self.special_squares.remove(sq)
                break
        
        # Check for teleporter
        for sq in self.special_squares:
            if sq.square_type == 'teleporter_in' and sq.position == move.to_pos:
                if sq.pair_position and not self.get_piece(sq.pair_position):
                    self.board[sq.pair_position[0]][sq.pair_position[1]] = piece
                    self.board[move.to_pos[0]][move.to_pos[1]] = None
                    break
        
        self.move_history.append(move)
        self.move_count += 1
        self.time_dilation_counter += 1
        
        # Check for time dilation (every 10 moves)
        if self.time_dilation_counter % 10 == 0:
            self.extra_move_available = True
        else:
            self.extra_move_available = False
            self.current_player = Color.BLACK if self.current_player == Color.WHITE else Color.WHITE
        
        return True
    
    def is_in_check(self, color: Color) -> bool:
        """Check if king of given color is in check"""
        # Find king
        king_pos = None
        for r in range(self.board_size):
            for c in range(self.board_size):
                piece = self.board[r][c]
                if piece and piece.piece_type == PieceType.KING and piece.color == color:
                    king_pos = (r, c)
                    break
        
        if not king_pos:
            return False
        
        # Check if any opponent piece can capture king
        opponent = Color.BLACK if color == Color.WHITE else Color.WHITE
        for r in range(self.board_size):
            for c in range(self.board_size):
                piece = self.board[r][c]
                if piece and piece.color == opponent:
                    moves = self.get_pseudo_legal_moves((r, c))
                    if any(m.to_pos == king_pos for m in moves):
                        return True
        
        return False
    
    def get_legal_moves(self, color: Color) -> List[Move]:
        """Get all legal moves for given color"""
        legal_moves = []
        
        for r in range(self.board_size):
            for c in range(self.board_size):
                piece = self.board[r][c]
                if piece and piece.color == color:
                    moves = self.get_pseudo_legal_moves((r, c))
                    for move in moves:
                        # Make move temporarily
                        temp_state = self.copy()
                        temp_state.board[move.to_pos[0]][move.to_pos[1]] = piece
                        temp_state.board[move.from_pos[0]][move.from_pos[1]] = None
                        
                        if not temp_state.is_in_check(color):
                            legal_moves.append(move)
        
        return legal_moves
    
    def copy(self) -> 'GameState':
        """Create a deep copy of the game state"""
        new_state = GameState(self.board_size)
        new_state.board = [[p for p in row] for row in self.board]
        new_state.current_player = self.current_player
        new_state.move_count = self.move_count
        new_state.special_squares = self.special_squares.copy()
        new_state.time_dilation_counter = self.time_dilation_counter
        new_state.extra_move_available = self.extra_move_available
        return new_state
    
    def evaluate(self) -> float:
        """Evaluate position from white's perspective"""
        piece_values = {
            PieceType.PAWN: 1,
            PieceType.KNIGHT: 3,
            PieceType.BISHOP: 3.25,
            PieceType.ROOK: 5,
            PieceType.QUEEN: 9,
            PieceType.KING: 0
        }
        
        score = 0
        
        for r in range(self.board_size):
            for c in range(self.board_size):
                piece = self.board[r][c]
                if piece:
                    value = piece_values[piece.piece_type]
                    
                    # Position bonus
                    center_bonus = 0
                    dist_from_center = abs(r - self.board_size/2) + abs(c - self.board_size/2)
                    center_bonus = max(0, 0.1 * (self.board_size - dist_from_center))
                    
                    if piece.color == Color.WHITE:
                        score += value + center_bonus
                    else:
                        score -= value + center_bonus
        
        return score
    
    def display(self):
        """Display the board"""
        print("\n  " + " ".join(str(i) for i in range(self.board_size)))
        for r in range(self.board_size - 1, -1, -1):
            row_str = f"{r} "
            for c in range(self.board_size):
                piece = self.board[r][c]
                if piece:
                    row_str += str(piece) + " "
                else:
                    # Check for special squares
                    special = False
                    for sq in self.special_squares:
                        if sq.position == (r, c):
                            if sq.square_type == 'bomb':
                                row_str += "X "
                            elif sq.square_type == 'teleporter_in':
                                row_str += "T "
                            elif sq.square_type == 'teleporter_out':
                                row_str += "t "
                            special = True
                            break
                    if not special:
                        row_str += ". "
            print(row_str)
        print(f"\nMove: {self.move_count}, Current player: {self.current_player.name}")

# ChessAI implementation moved to assignment tasks
# Participants are required to implement their own AI with alpha-beta pruning.

def generate_test_positions(board_size: int = 8, num_positions: int = 50) -> List[Dict]:
    """Generate test positions for evaluation"""
    positions = []
    
    for i in range(num_positions):
        state = GameState(board_size)
        state.initialize_standard()
        
        # Add random special squares
        if board_size >= 8:
            # Add bombs
            bomb_positions = random.sample(
                [(r, c) for r in range(2, board_size - 2) for c in range(board_size)],
                min(3, (board_size - 4) * board_size)
            )
            state.add_bombs(bomb_positions[:3])
            
            # Add teleporters
            teleporter_pairs = []
            for _ in range(2):
                pos1 = (random.randint(2, board_size - 3), random.randint(0, board_size - 1))
                pos2 = (random.randint(2, board_size - 3), random.randint(0, board_size - 1))
                teleporter_pairs.append((pos1, pos2))
            state.add_teleporters(teleporter_pairs)
        
        # Make some random moves
        num_moves = random.randint(5, 20)
        for _ in range(num_moves):
            moves = state.get_legal_moves(state.current_player)
            if moves:
                move = random.choice(moves)
                state.make_move(move)
        
        positions.append({
            'id': i,
            'board_size': board_size,
            'fen': str(state.board),  # Simplified FEN
            'current_player': state.current_player.name,
            'move_count': state.move_count,
            'special_squares': [
                {'type': sq.square_type, 'pos': sq.position}
                for sq in state.special_squares
            ]
        })
    
    return positions

if __name__ == '__main__':
    # Demo game
    print("=== Infinite Chess Grandmaster Demo ===\n")
    
    # Create 10x10 board
    game = GameState(10)
    game.initialize_standard()
    
    # Add special features
    game.add_bombs([(4, 4), (5, 5), (6, 6)])
    game.add_teleporters([((3, 3), (7, 7)), ((3, 6), (7, 3))])
    
    game.display()
    
    # Generate test positions
    print("\n=== Generating Test Positions ===")
    positions = generate_test_positions(8, 10)
    print(f"Generated {len(positions)} test positions")
    
    # Save test positions
    with open('test_positions.json', 'w') as f:
        json.dump(positions, f, indent=2)
    print("Saved to test_positions.json")
