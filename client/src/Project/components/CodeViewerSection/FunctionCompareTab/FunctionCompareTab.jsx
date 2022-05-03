import React from 'react';
import {parseDiff, Diff, Hunk, Decoration} from 'react-diff-view';
import 'react-diff-view/style/index.css';
import {diffLines, formatLines} from 'unidiff';

function FunctionCompareTab() {
    const oldText = 'const bib = () => {\n\tconst a = 1\n\tconsole.log(\'wawawewa\')\n}';
    const newText = 'const bib = () => {\n\tconst a = 1\n\tconsole.log(\'wowawowa\')\n}';
    const diffTest = parseDiff(formatLines(diffLines(oldText, newText), {context:3}));

    const renderFile = ({oldPath, newPath, oldRevision, newRevision, type, hunks}) => (
        <div key={oldRevision + '-' + newRevision} className="file-diff">
            <header className="diff-header">{oldPath === newPath ? oldPath : `${oldPath} -> ${newPath}`}</header>
            <Diff viewType="split" diffType={type} hunks={hunks}>
                {hunks =>
                    hunks.map(hunk => [
                        <Decoration key={'deco-' + hunk.content}>
                            <div className="hunk-header">{hunk.content}</div>
                        </Decoration>,
                        <Hunk key={hunk.content} hunk={hunk} />,
                    ])
                }
            </Diff>
        </div>
    );

    return (
        <div>
            {diffTest.map(renderFile)}
        </div>
    );
}

export default FunctionCompareTab;