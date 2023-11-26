import React from 'react';
import * as ReactDOMClient from 'react-dom/client';
import Othello from './othello';

const container = document.getElementById(VISUALIZER_INSTANCE_ID);
const root = ReactDOMClient.createRoot(container);
const onUpdateFromControl = (descriptor) => {
    console.log('rendering', descriptor);
    root.render(<Othello player = {descriptor.player} board = {descriptor.board} win = {descriptor.win}/>);
}
console.log('connecting to control');
WEBGME_CONTROL.registerUpdate(onUpdateFromControl);