import React from 'react';

import {useSelector, useDispatch} from "react-redux";
import {selectFunctionList} from '../../../../reducers/functionListSlice';
import {setActiveFunction} from "../../../../reducers/activeFunctionSlice";
import {selectActiveFunction} from "../../../../reducers/activeFunctionSlice";
import {setActiveTestEmpty} from "../../../../reducers/activeTestInfoSlice";

import CustomTab from "../../../../shared/components/Tab";
import {isEmpty} from "lodash";

function functionTabGenerator() {

    const dispatch = useDispatch();
    const functionList = useSelector(selectFunctionList);
    const activeFunction = useSelector(selectActiveFunction);

    function isActiveFunction(funcInfo) {

        return (!isEmpty(activeFunction)) &&
            (activeFunction.pathToProject === funcInfo.pathToProject) &&
            (activeFunction.fileId === funcInfo.fileId) &&
            (activeFunction.functionId === funcInfo.functionId);
    }

    return (
        <CustomTab label='Function Tab'>
            <div>Function Tab</div>
            <table>
                <thead>
                <tr>
                    <th>Function Name</th>
                    <th>File Name</th>
                    <th>Dependencies</th>
                    <th>Number of tests</th>
                </tr>
                </thead>
                <tbody>
                {functionList.map(functionInfo => {
                    return (
                        <tr
                            key={functionInfo._id}
                            onClick={() => {
                                dispatch(setActiveFunction(functionInfo));
                                dispatch(setActiveTestEmpty());
                            }}
                            className= {isActiveFunction(functionInfo)?"active-function-info":""}
                        >
                            <td>{functionInfo.functionId}</td>
                            <td>{functionInfo.fileId}</td>
                            <td>{functionInfo.dependencies}</td>
                            <td>{functionInfo.numberOfTests}</td>
                        </tr>
                    );
                })}
                </tbody>
            </table>
        </CustomTab>
    );
}


export default functionTabGenerator;