import React, {useState, useEffect} from 'react';


function CustomTab({label, children}) {

    //const [tabLabel, setTabLabel] = useState(label);

    return (
        <div className={'tab ' + label} >
            {children}
        </div>
    );
}

export default CustomTab;