import React, {useState, useEffect} from 'react';
import {useDispatch, useSelector} from "react-redux";
import {selectUnsavedActiveTest, updateException} from "../../../../reducers/activeTestInfoSlice";
import ShouldEqualSelector from "../../../../shared/components/ShouldEqualSelector";
import './ExceptionTab.scss';
import {isEmpty, cloneDeep} from "lodash";

function ExceptionTab({}) {

    const dispatch = useDispatch();
    const unsavedTest = useSelector(selectUnsavedActiveTest);

    const [exceptionNameErrorMessage, setExceptionNameErrorMessage] = useState('');
    const [exceptionMessageErrorMessage, setExceptionMessageErrorMessage] = useState('');

    //const [exceptionNameCheck, setExceptionNameCheck] = useState(undefined);
    //const [exceptionMessageCheck, setExceptionMessageCheck] = useState(undefined);

    function onChangeCallback(exception) {
        dispatch(updateException(exception));
    }

    useEffect(() => {
        if (unsavedTest.moduleData.exception.value !== undefined) {
            if (validExceptionName(unsavedTest.moduleData.exception.value)) {
                setExceptionNameErrorMessage('');
            }
        }

        if (unsavedTest.moduleData.exception.message !== undefined) {
            if (ValidExceptionMessage(unsavedTest.moduleData.exception.message)) {
                setExceptionMessageErrorMessage('');
            }
        }
    }, [unsavedTest.moduleData.exception])


    function validExceptionName(exceptionName) {
        if (exceptionName === '') {
            setExceptionNameErrorMessage("Exception name can't be empty, either disable it or provide a name.");
            return false;
        }
        const validName = exceptionName.match(/(^\d+|[^\w$]+)/g);
        if (validName !== null) {
            setExceptionNameErrorMessage('Exception name contains illegal characters');
            return false;
        }
        return true;
    }

    function ValidExceptionMessage(exceptionMessage) {
        //if (exceptionMessageCheck) {
            if (exceptionMessage === '') {
                setExceptionMessageErrorMessage("Exception message can't be empty, either disable it or provide a message.")
                return false;
            }
        //}
        return true;
    }

    function onExceptionNameChangeCallback(e) {
        e.preventDefault();
        const exceptionClone = cloneDeep(unsavedTest.moduleData.exception);
        exceptionClone.value = e.target.value;
        onChangeCallback(exceptionClone);
    }

    function onExceptionMessageChangeCallback(e) {
        e.preventDefault();
        const exceptionClone = cloneDeep(unsavedTest.moduleData.exception);
        exceptionClone.message = e.target.value;
        onChangeCallback(exceptionClone);
    }

    function onExceptionEqualChangeCallback(e) {
        e.preventDefault();
        const exceptionClone = cloneDeep(unsavedTest.moduleData.exception);
        exceptionClone.equal = (e.target.value === 'true');
        onChangeCallback(exceptionClone);
    }

    function onCheckExceptionNameCallback(e) {
        e.preventDefault();
        const exceptionClone = cloneDeep(unsavedTest.moduleData.exception);
        if (exceptionClone.value !== undefined) {
            delete exceptionClone.value;
            setExceptionNameErrorMessage('');
        } else {
            exceptionClone.value = '';
        }
        onChangeCallback(exceptionClone);
    }

    function onCheckExceptionMessageCallback(e) {
        e.preventDefault();
        const exceptionClone = cloneDeep(unsavedTest.moduleData.exception);
        if (exceptionClone.message !== undefined) {
            delete exceptionClone.message;
            setExceptionMessageErrorMessage('');
        } else {
            exceptionClone.message = '';
        }
        onChangeCallback(exceptionClone);
    }

    if (isEmpty(unsavedTest)) {
        return <div className="test-creator-tab-empty">waiting...</div>
    }

    return (
        <div className="exception-tab-wrapper">
            <form
                className ="h-100"
                onSubmit={e => e.preventDefault()}
            >
                <ShouldEqualSelector
                    value={unsavedTest.moduleData.exception.equal}
                    onChange={onExceptionEqualChangeCallback}
                    shouldEqualLabel={'Should Be Thrown'}
                    shouldNotEqualLabel={'Should Not Be Thrown'}
                />
                <div className ="input-group exception-tab-exception-name">

                    <div className="input-group-text">
                        <input
                            key ={'exception-tab-exception-name' + (unsavedTest.moduleData.exception.value !== undefined)}
                            className="form-check-input"
                            type="checkbox"
                            checked={(unsavedTest.moduleData.exception.value !== undefined)}
                            onChange={onCheckExceptionNameCallback}
                        />
                    </div>
                        <span className="input-group-text">Name</span>
                        <input
                            type="text"
                            className="form-control"
                            value={(unsavedTest.moduleData.exception.value) || ''}
                            onChange={onExceptionNameChangeCallback}
                            disabled={(unsavedTest.moduleData.exception.value === undefined)}
                        />

                </div>
                {(exceptionNameErrorMessage !== '') && (
                    <div className ="alert alert-danger exception-tab-exception-name-alert">
                        {exceptionNameErrorMessage}
                    </div>
                )}
                <div className ="input-group exception-tab-exception-message">
                    <div className="input-group-text">
                        <input
                            key ={'exception-tab-exception-name' + (unsavedTest.moduleData.exception.message !== undefined)}
                            className="form-check-input"
                            type="checkbox"
                            checked={(unsavedTest.moduleData.exception.message !== undefined)}
                            onChange={onCheckExceptionMessageCallback}
                        />
                    </div>
                    <span className="input-group-text">Message</span>
                    <input
                        type="text"
                        className="form-control"
                        value={(unsavedTest.moduleData.exception.message) || ''}
                        onChange={onExceptionMessageChangeCallback}
                        disabled={(unsavedTest.moduleData.exception.message === undefined)}
                    />
                </div>
                {(exceptionMessageErrorMessage !== '') && (
                    <div className ="alert alert-danger exception-tab-exception-message-alert">
                        {exceptionMessageErrorMessage}
                    </div>
                )}
            </form>
        </div>
    );
}

export default ExceptionTab;