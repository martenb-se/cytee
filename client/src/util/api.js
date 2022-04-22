
 function updateTime(setCurrentTimeCallback) {
    fetch('/api/time').then(res => res.json()).then(data => {
        setCurrentTimeCallback(data.time);
    });
}

 export {updateTime}
