# Chess Basics for Agents

## Board Representation

FEN (Forsyth-Edwards Notation) describes a position:
```
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
```

Parts:
1. Piece placement (rank 8 to rank 1)
2. Active color (w/b)
3. Castling rights (KQkq or -)
4. En passant square (or -)
5. Halfmove clock (for 50-move rule)
6. Fullmove number

## Algebraic Notation

- Files: a-h (left to right from white's view)
- Ranks: 1-8 (bottom to top from white's view)
- Pieces: K (King), Q (Queen), R (Rook), B (Bishop), N (Knight)
- Pawns: no letter, just the square

Examples:
- e4: pawn to e4
- Nf3: knight to f3
- Bxc6: bishop captures on c6
- O-O: kingside castle
- e8=Q: pawn promotes to queen
- Qh7#: queen to h7, checkmate

## Basic Evaluation

Material values (standard):
- Queen: 9
- Rook: 5
- Bishop: 3
- Knight: 3
- Pawn: 1

Position factors:
- King safety (castled is usually safer)
- Piece activity (developed pieces, open lines)
- Pawn structure (doubled, isolated, passed pawns)
- Center control (e4, d4, e5, d5)

## Opening Principles

1. Control the center (e4, d4)
2. Develop pieces (knights before bishops usually)
3. Castle early (king safety)
4. Connect rooks
5. Don't move the same piece twice
6. Don't bring queen out early

## Tactical Patterns

- Fork: one piece attacks two
- Pin: piece can't move without exposing more valuable piece
- Skewer: attack through one piece to another
- Discovery: moving one piece reveals attack from another
- Back rank mate: king trapped by own pawns

## Endgame Basics

- King becomes active in endgame
- Passed pawns are valuable
- Rook behind passed pawn
- Opposition (kings facing each other)
- K+R vs K: methodical push to edge
