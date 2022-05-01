import React from 'react';
import {useDispatch, useSelector} from "react-redux";
import {selectUnsavedActiveTest, updateException} from "../../../../reducers/activeTestInfoSlice";

function ExceptionTab({label}) {

    const dispatch = useDispatch();
    const unsavedTest = useSelector(selectUnsavedActiveTest);

    function changeExceptionCallback(e) {
        e.preventDefault();
        const exceptionClone = cloneDeep(e.target.value);
        dispatch(updateException(exceptionClone));
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