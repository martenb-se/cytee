import React from 'react';
import {selectUnsavedActiveTest, updateReturnValue} from "../../../../reducers/activeTestInfoSlice";
import {useDispatch, useSelector} from "react-redux";

import cloneDeep from "lodash/cloneDeep";

import ArgumentTypeSelector from "../../../../shared/components/ArgumentTypeSelector";
import ArgumentDataFieldInput from "../../../../shared/components/ArgumentInputValueSelector";
import {isEmpty} from "lodash";

function ReturnTab({label}) {

    const dispatch = useDispatch();
    const unsavedTest = useSelector(selectUnsavedActiveTest);

    function onChangeCallback(returnValue) {
        dispatch(updateReturnValue(returnValue));
    }

    if (isEmpty(unsavedTest) ||
        (unsavedTest.moduleData === undefined) ||
        (unsavedTest.moduleData.returnValue === undefined)) {
        return <div className ="test-creator-tab-empty">waiting...</div>
    }

    function changeReturnValueTypeCallback(e) {
        const returnValueClone = cloneDeep(unsavedTest.moduleData.returnValue);
        returnValueClone.type = e.target.value;
        switch(returnValueClone.type) {
            case 'undefined':
            case 'null':
                delete returnValueClone.value;
                break;
            case 'array':
                returnValueClone.value = [];
                break;
            case 'boolean':
                returnValueClone.value = false;
                break;
            case 'number':
                returnValueClone.value = 0;
                break;
            case 'string':
                returnValueClone.value = '';
                break;
            case 'object':
                returnValueClone.value = {};
                break;
        }

        onChangeCallback(returnValueClone);
    }

    function changeReturnValueCallback(e) {
        e.preventDefault();
        const returnValueClone = cloneDeep(unsavedTest.moduleData.returnValue);
        returnValueClone.value = e.target.value;
        onChangeCallback(returnValueClone);
    }

    return (
            <div className="return-value-tab-wrapper">
                <form
                    onSubmit={e => e.preventDefault()}
                >
                    <label
                        className="form-label"
                        htmlFor={"return-value-tab-type-field"}
                    >
                        Return Value
                    </label>
                    <div className="input-group">
                        <ArgumentTypeSelector
                            id={"return-value-tab-type-field"}
                            type={unsavedTest.moduleData.returnValue.type}
                            onChangeCallback={changeReturnValueTypeCallback}
                        />
                        <ArgumentDataFieldInput
                            type={unsavedTest.moduleData.returnValue.type}
                            value={unsavedTest.moduleData.returnValue.value}
                            onChangeCallback={changeReturnValueCallback}
                        />
                    </div>
                </form>
            </div>
    );
}

export default ReturnTab;

/*
import React, {useContext, useEffect} from 'react';

// lodash helpers
import cloneDeep from "lodash/cloneDeep";

// components
import CustomTab from "../../../../shared/components/Tab";
import ArgumentTypeSelector from "../../../../shared/components/ArgumentTypeSelector";
import ArgumentDataFieldInput from "../../../../shared/components/ArgumentInputValueSelector";

import {unsavedTestInfoContext} from "../TestCreatorSection";

function returnTabGenerator() {

    const [state, dispatch] = useContext(unsavedTestInfoContext);

    useEffect(() => {
        console.log('state: ', state);
    }, [state])

    function changeReturnValueTypeCallback(e) {
        const returnValueClone = cloneDeep(state.moduleData.returnValue);
        returnValueClone.type = e.target.value;
        switch(returnValueClone.type) {
            case 'undefined':
            case 'null':
                delete returnValueClone.value;
                break;
            case 'array':
                returnValueClone.value = [];
                break;
            case 'boolean':
                returnValueClone.value = false;
                break;
            case 'number':
                returnValueClone.value = 0;
                break;
            case 'string':
                returnValueClone.value = '';
                break;
            case 'object':
                returnValueClone.value = {};
                break;
        }

        dispatch({
            type: 'returnValue/updateReturnValue',
            payload: returnValueClone,
        })
    }

    function changeReturnValueCallback(e) {
        const returnValueClone = cloneDeep(state.moduleData.returnValue);
        returnValueClone.value = e.target.value;
        dispatch({
            type: 'returnValue/updateReturnValue',
            payload: returnValueClone,
        })
    }

    return (
       <CustomTab label='Return value'>
           <div>
               <h1>Return Value Tab</h1>
               <div>
                   <span>Return Value</span>
                   <ArgumentTypeSelector
                       type={state.moduleData.returnValue.type}
                       onChangeCallback={changeReturnValueTypeCallback}
                   />
                   <ArgumentDataFieldInput
                       type={state.moduleData.returnValue.type}
                       value={state.moduleData.returnValue.value}
                       onChangeCallback={changeReturnValueCallback}
                   />
               </div>
           </div>
       </CustomTab>
    );
}

export default returnTabGenerator;

 */