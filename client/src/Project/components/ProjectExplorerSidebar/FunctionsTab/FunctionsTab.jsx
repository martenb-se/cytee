import React from 'react';
import {useSelector, useDispatch} from "react-redux";
import {selectFunctionList} from '../../../../reducers/functionListSlice';
import {setActiveFunction} from "../../../../reducers/activeFunctionSlice";
import {createEmptyActiveTest} from "../../../../reducers/activeTestInfoSlice";

import CustomTab from "../../../../shared/components/Tab";

function functionTabGenerator() {

    const dispatch = useDispatch();
    const functionList = useSelector(selectFunctionList);

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
                        <tr key={functionInfo._id} onClick={() => {
                            dispatch(setActiveFunction(functionInfo));
                            dispatch(createEmptyActiveTest(functionInfo));
                        }}>
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