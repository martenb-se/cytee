import React, {useEffect, useState} from 'react';

import SyntaxHighlighter from "react-syntax-highlighter";
import {monokai} from "react-syntax-highlighter/src/styles/hljs";

import {isEmpty} from "lodash";
import {getFunction} from "../../../../util/api";
import {useSelector} from "react-redux";
import {selectActiveFunction} from "../../../../reducers/activeFunctionSlice";

import './FunctionCodeTab.scss';

function FunctionCodeTab() {

    const [functionCode, setFunctionCode] = useState(undefined);
    const activeFunc = useSelector(selectActiveFunction);

    const projectPath = useSelector(state => state.project.path);

    useEffect(() => {
        if (!isEmpty(activeFunc) ) {
            getFunction(projectPath, activeFunc.fileId).then(data => {
                setFunctionCode(data.fileContents);
            });
        }
    }, [activeFunc])



    return (
        <>
            {
                (functionCode !== undefined) &&
                <div className={'functionCodeView'}>
                    <SyntaxHighlighter
                        language="javascript"
                        className = "function-code-view"
                        style={monokai}
                        showLineNumbers={true}
                        wrapLines={true}
                    >
                        {functionCode}
                    </SyntaxHighlighter>
                </div>
            }
        </>
    )
}

export default FunctionCodeTab;