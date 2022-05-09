import React, {useEffect, useState} from 'react';
import {Decoration, Diff, Hunk, parseDiff} from 'react-diff-view';
import 'react-diff-view/style/index.css';
import {diffLines, formatLines} from 'unidiff';
import {useSelector} from "react-redux";
import {selectActiveFunction} from "../../../../reducers/activeFunctionSlice";
import {getFunction, getOldFunction} from "../../../../util/api";
import LoadingComponent from "../../../../shared/components/LoadingComponent";

import './FunctionCodeCompareTab.scss';

function FunctionCompareTab({}) {

    const [newText, setNewText] = useState('');
    const [oldText, setOldText] = useState('');
    const [diffTest, setDiffText] = useState(undefined);

    const [newCodeLoadingState, setNewCodeLoadingState] = useState('');
    const [oldCodeLoadingState, setOldCodeLoadingState] = useState('');

    const activeFunction = useSelector(selectActiveFunction);
    const projectPath = useSelector(state => state.project.path);

    useEffect(() => {
        setNewCodeLoadingState('loading');
        getFunction(projectPath, activeFunction.fileId).then(data => {
            setNewText(data.fileContents);
            setNewCodeLoadingState('done');
        })
    }, [activeFunction]);

    useEffect(() => {
        if (newCodeLoadingState === 'done') {
            setOldCodeLoadingState('loading');
            getOldFunction(projectPath, activeFunction.fileId).then(data => {
                setOldText(data.fileContents)
                setOldCodeLoadingState('done');
            });
        }
    }, [newCodeLoadingState])

    useEffect(() => {
        if (oldCodeLoadingState === 'done') {
            setDiffText(parseDiff(formatLines(diffLines(oldText, newText), {context: 3})));
        }
    }, [oldCodeLoadingState])

    if ((newCodeLoadingState === 'loading') || (oldCodeLoadingState === 'loading')) {
        return <div className="code-compare-loading-view"><LoadingComponent/></div>
    }

    if (diffTest === undefined) {
        return <div></div>
    }

    const renderFile = ({oldPath, newPath, oldRevision, newRevision, type, hunks}) => (
        <div key={oldRevision + '-' + newRevision} className="code-compare-file-diff">
            <header className="diff-header">{oldPath === newPath ? oldPath : `${oldPath} -> ${newPath}`}</header>
            <Diff viewType="split" diffType={type} hunks={hunks}>
                {hunks =>
                    hunks.map(hunk => [
                        <Decoration key={'deco-' + hunk.content}>
                            <div className="hunk-header">{hunk.content}</div>
                        </Decoration>,
                        <Hunk key={hunk.content} hunk={hunk}/>,
                    ])
                }
            </Diff>
        </div>
    );

    return (
        <div className="function-compare-tab-wrapper">
            {diffTest.map(renderFile)}
        </div>
    );
}

export default FunctionCompareTab;