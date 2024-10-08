/*globals define*/
/*eslint-env node, browser*/

/**
 * Generated by PluginGenerator 2.20.5 from webgme on Fri Jul 21 2023 23:41:07 GMT-0500 (Central Daylight Time).
 * A plugin that inherits from the PluginBase. To see source code documentation about available
 * properties and methods visit %host%/docs/source/PluginBase.html.
 */

define([
    'plugin/PluginConfig',
    'text!./metadata.json',
    'plugin/PluginBase',
    'Othello_Game_Design_Studio/utils',
    'Othello_Game_Design_Studio/constants'
], function (
    PluginConfig,
    pluginMetadata,
    PluginBase,
    UTILS,
    CONSTANTS) {
    'use strict';

    pluginMetadata = JSON.parse(pluginMetadata);

    function CheckWinCondition() {
        PluginBase.call(this);
        this.pluginMetadata = pluginMetadata;
    }

    CheckWinCondition.metadata = pluginMetadata;
    CheckWinCondition.prototype = Object.create(PluginBase.prototype);
    CheckWinCondition.prototype.constructor = CheckWinCondition;

    CheckWinCondition.prototype.main = function (callback) {
        const {core, META, logger, activeNode, result} = this;

        core.loadSubTree(activeNode)
        .then(nodes => {
            const nodeHash = {};
            nodes.forEach(node => {
                nodeHash[core.getPath(node)] = node;
            });

            let boardNode = null;
            core.getChildrenPaths(activeNode).forEach(path => {
                const node = nodeHash[path];
                if(core.isInstanceOf(node, META.Board)) {
                   boardNode = node;
                }
            });

            if (!boardNode) {
                logger.error('No Board node found.');
                result.setSuccess(false);
                callback(new Error('No Board node found.'), result);
                return;
            }

            const board = UTILS.getBoardDescriptor(core, META, boardNode, nodeHash);
            const winner = this.checkOthelloWinner(board);

            if (winner) {
                this.createMessage(activeNode, 'Winner: ' + winner);
            } else {
                this.createMessage(activeNode, 'No winner yet.');
            }

            result.setSuccess(true);
            callback(null, result);
        })
        .catch(error => {
            logger.error(error);
            result.setSuccess(false);
            callback(error, result);
        });
    };

    CheckWinCondition.prototype.checkOthelloWinner = function (board) {
        // In Othello, the winner is the player with the majority of pieces on the board
        // when no more moves are possible.
        const pieceCounts = {
            [CONSTANTS.PIECE.BLACK]: 0,
            [CONSTANTS.PIECE.WHITE]: 0
        };

        board.forEach(row => {
            row.forEach(piece => {
                if (piece === CONSTANTS.PIECE.BLACK || piece === CONSTANTS.PIECE.WHITE) {
                    pieceCounts[piece]++;
                }
            });
        });

        // Determine winner
        if (pieceCounts[CONSTANTS.PIECE.BLACK] + pieceCounts[CONSTANTS.PIECE.WHITE] === CONSTANTS.BOARD_SIZE * CONSTANTS.BOARD_SIZE || !UTILS.hasValidMoves(board)) {
            return pieceCounts[CONSTANTS.PIECE.BLACK] > pieceCounts[CONSTANTS.PIECE.WHITE] ? CONSTANTS.PLAYER.BLACK : CONSTANTS.PLAYER.WHITE;
        }

        return null; // No winner yet
    };

    return CheckWinCondition;
});
