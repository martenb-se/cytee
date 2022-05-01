import React, {useEffect, useState} from 'react';

import SyntaxHighlighter from "react-syntax-highlighter";
import {monokai} from "react-syntax-highlighter/src/styles/hljs";

import {isEmpty} from "lodash";
import {getFunction} from "../../../../util/api";
import {useSelector} from "react-redux";
import {selectActiveFunction} from "../../../../reducers/activeFunctionSlice";

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
        <div className={'functionCodeView'}>
            {(functionCode === undefined) ?
                <div>
                    Fetching function code...
                </div>
                :
                <SyntaxHighlighter language="javascript" style={monokai}>
                    {functionCode}
                </SyntaxHighlighter>
            }
        </div>
    )
}

export default FunctionCodeTab;