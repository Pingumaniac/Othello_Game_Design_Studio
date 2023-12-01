define([], function () {
    return {
        // Define the two players
        PLAYER: {
            BLACK: 'BLACK',
            WHITE: 'WHITE'
        },

        // Define the piece states
        PIECE: {
            BLACK: 'B', // Representing black piece
            WHITE: 'W', // Representing white piece
            EMPTY: '-' // Empty space on the board
        },

        // Size of the Othello board
        BOARD_SIZE: 8,

        // Initial board setup
        INITIAL_BOARD: [
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['-', '-', '-', 'W', 'B', '-', '-', '-'],
            ['-', '-', '-', 'B', 'W', '-', '-', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-']
        ]
    }
});
