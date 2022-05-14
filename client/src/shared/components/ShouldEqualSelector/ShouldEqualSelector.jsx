import React from 'react';

import './ShouldEqualSelector.scss';

function ShouldEqualSelector({value, onChange, shouldEqualLabel, shouldNotEqualLabel}) {
    return (
      <div className ="input-group should-equal-selector">
          <span className="input-group-text">
              Matcher
          </span>
          <select
            className="form-select"

            value={value}
            onChange={onChange}
          >
              <option value={"true"}>{shouldEqualLabel}</option>
              <option value={"false"}>{shouldNotEqualLabel}</option>
          </select>
      </div>
    );
}

export default ShouldEqualSelector;