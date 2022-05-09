import React from 'react';
import {useDispatch, useSelector} from "react-redux";
import {selectUnsavedActiveTest, updateException} from "../../../../reducers/activeTestInfoSlice";

function ExceptionTab({}) {

    const dispatch = useDispatch();
    const unsavedTest = useSelector(selectUnsavedActiveTest);

    function changeExceptionCallback(e) {
        e.preventDefault();
        dispatch(updateException(e.target.value));
    }

    return (
      <div className="return-value-tab-wrapper h-100">
          <form
            onSubmit={e => e.preventDefault()}
            className="h-100"
          >
              <label
                  className="form-label"
                  htmlFor={"return-value-tab-type-field"}
              >
                  Exception
              </label>
              <div className ="input-group">
                  <input
                      type="text"
                      className="form-control"
                      value={unsavedTest.moduleData.exception.value}
                      onChange={changeExceptionCallback}
                  />
              </div>
          </form>
      </div>
    );
}

export default ExceptionTab;