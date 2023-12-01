define(['./constants'], function (CONSTANTS) {
    return {
        getBoardDescriptor: (core, META, boardNode, nodeHash) => {
            // Initialize an 8x8 board with all empty pieces
            const board = Array(CONSTANTS.BOARD_SIZE).fill(null).map(() => Array(CONSTANTS.BOARD_SIZE).fill(CONSTANTS.PIECE.EMPTY));

            // Populate the board with pieces
            core.getChildrenPaths(boardNode).forEach(tilePath => {
                const tileNode = nodeHash[tilePath];
                const row = core.getAttribute(tileNode, 'row');
                const col = core.getAttribute(tileNode, 'column');

                // Determine if the tile is a black or white piece
                const pieces = core.getChildrenPaths(tileNode);
                let pieceValue = CONSTANTS.PIECE.EMPTY;
                if (pieces.length > 0) {
                    pieceValue = core.isInstanceOf(nodeHash[pieces[0]], META.OthelloBlackPiece) ? 
                        CONSTANTS.PIECE.BLACK : CONSTANTS.PIECE.WHITE;
                }

                // Place the piece on the board
                board[row][col] = pieceValue;
            });

            return board;
        },

        getPositionHash: (core, boardNode, nodeHash) => {
            const hash = {};
            core.getChildrenPaths(boardNode).forEach(tilePath => {
                const tileNode = nodeHash[tilePath];
                const row = core.getAttribute(tileNode, 'row');
                const col = core.getAttribute(tileNode, 'column');
                const position = row * CONSTANTS.BOARD_SIZE + col; // Convert 2D position to 1D index
                hash[position] = core.getPath(tileNode);
            });
            return hash;
        }
    }
});
