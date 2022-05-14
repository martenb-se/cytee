import React, {useState, useEffect} from 'react';
import {useDispatch, useSelector} from "react-redux";
import {selectActiveTest, selectUnsavedActiveTest, updateException} from "../../../../reducers/activeTestInfoSlice";
import './ExceptionTab.scss';
import {isEmpty} from "lodash";

function ExceptionTab({}) {

    const dispatch = useDispatch();
    const unsavedTest = useSelector(selectUnsavedActiveTest);
    const activeTest = useSelector(selectActiveTest);

    const [exceptionName, setExceptionName] = useState(
        (isEmpty(activeTest))?
            unsavedTest.moduleData.exception.value:activeTest.moduleData.exception.value
    );
    const [exceptionMessage, setExceptionMessage] = useState(
        (isEmpty(activeTest))?
        unsavedTest.moduleData.exception.message:activeTest.moduleData.exception.message
    );

    const [exceptionNameCheck, setExceptionNameCheck] = useState(exceptionName !== '');
    const [exceptionMessageCheck, setExceptionMessageCheck] = useState(exceptionMessage !== '');

    const [exceptionNameErrorMessage, setExceptionNameErrorMessage] = useState('');
    const [exceptionMessageErrorMessage, setExceptionMessageErrorMessage] = useState('');

    useEffect(() => {
        if (!isEmpty(activeTest)) {
            setExceptionName(activeTest.moduleData.exception.value);
            setExceptionNameCheck(activeTest.moduleData.exception.value !== '');
            setExceptionMessage(activeTest.moduleData.exception.message);
            setExceptionMessageCheck(activeTest.moduleData.exception.message !== '');
        }
    }, [activeTest])

    useEffect(() => {

        if (validExceptionName(exceptionName))
            setExceptionNameErrorMessage('');

        if (ValidExceptionMessage(exceptionMessage))
            setExceptionMessageErrorMessage('');

        dispatch(updateException({
            name: exceptionName,
            message: exceptionMessage
        }));
    }, [exceptionName, exceptionMessage]);

    useEffect(() => {
        if (!exceptionNameCheck)
            setExceptionName('');
        else
            if ((!isEmpty(activeTest)) && (activeTest.moduleData.exception.value !== ''))
                setExceptionName(activeTest.moduleData.exception.value);
    }, [exceptionNameCheck])

    useEffect(() => {
        if (!exceptionMessageCheck)
            setExceptionMessage('');
        else
        if ((!isEmpty(activeTest)) && (activeTest.moduleData.exception.message !== ''))
            setExceptionMessage(activeTest.moduleData.exception.message);
    }, [exceptionMessageCheck])

    function validExceptionName(exceptionName) {
        if (exceptionNameCheck) {
            if (exceptionName === '') {
                setExceptionNameErrorMessage("Exception name can't be empty, either disable it or provide a name.");
                return false;
            }

            const validName = exceptionName.match(/(^\d+|[^\w$]+)/g);
            if (validName !== null) {
                setExceptionNameErrorMessage('Exception name contains illegal characters');
                return false;
            }
        }
        return true;
    }

    function ValidExceptionMessage(exceptionMessage) {
        if (exceptionMessageCheck) {
            if (exceptionMessage === '') {
                setExceptionMessageErrorMessage("Exception message can't be empty, either disable it or provide a message.")
                return false;
            }
        }
        return true;
    }

    function onExceptionNameCallback(e) {
        e.preventDefault();
        setExceptionName(e.target.value);
    }

    function onExceptionMessageCallback(e) {
        e.preventDefault();
        setExceptionMessage(e.target.value);
    }

    return (
      <div className="exception-tab-wrapper h-100">
          <form
            onSubmit={e => e.preventDefault()}
            className="h-100"
          >
              <div className ="input-group exception-tab-exception-name">
                  <div className="input-group-text">
                      <input
                          key ={'exception-tab-exception-name' + exceptionNameCheck}
                          className="form-check-input"
                          type="checkbox"
                          checked={exceptionNameCheck}
                          onChange={e => {
                              e.preventDefault();
                              setExceptionNameErrorMessage('');
                              setExceptionNameCheck(!exceptionNameCheck);
                          }}
                      />
                  </div>
                  <span className="input-group-text">Name</span>
                  <input
                      type="text"
                      className="form-control"
                      value={exceptionName}
                      onChange={onExceptionNameCallback}
                      disabled={!exceptionNameCheck}
                  />
              </div>
              <div className ="input-group exception-tab-exception-message">
                  <div className="input-group-text">
                      <input
                          key ={'exception-tab-exception-message' + exceptionMessageCheck}
                          className="form-check-input"
                          type="checkbox"
                          checked={exceptionMessageCheck}
                          onChange={e => {
                              e.preventDefault();
                              setExceptionMessageErrorMessage('');
                              setExceptionMessageCheck(!exceptionMessageCheck);
                          }}
                      />

                  </div>
                  <span className="input-group-text">Message</span>
                  <input
                      type="text"
                      className="form-control"
                      value={exceptionMessage}
                      onChange={onExceptionMessageCallback}
                      disabled={!exceptionMessageCheck}
                  />
              </div>
              {(exceptionNameErrorMessage !== '') && (
                  <div className ="alert alert-danger exception-tab-exception-name-alert">
                      {exceptionNameErrorMessage}
                  </div>
              )}
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