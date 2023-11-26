import React, {useCallback, useState} from 'react';
import Board from './board';

export default function Othello({player, win, board}) {
    const getLabel = () => {
        
    }
    return (
    <div style={{ width: '100%', height: '100%', fontFamily:'fantasy', fontSize:'36px', fontWeight:'bold'}}>
        {getLabel()}
        <Board player={player} board={board} win={win}/>
    </div>
    );
}