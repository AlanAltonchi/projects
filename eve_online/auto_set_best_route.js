// What is this?
// The gatecheck website determines the safest route for you to take so that your ship is not destroyed by other players.
// Problem: In-game, you must manually set the optimal path provided by the website. System by system.
// Solution: This add-on will automatically import the ideal path into the game so that you do not have to manually click on 30+ star systems.

// Note: To automatically run JS code on websites, use an extension like Tampermonkey https://www.tampermonkey.net/
// Set the code below to automatically run when visiting https://eveeye.com/
setTimeout(() => {document.querySelector("#searchinput").value = "Bearer " + accessToken; navigator.clipboard.writeText(document.querySelector("#searchinput").value);
                      setTimeout(() =>{
                          close();
                      },50);
                     }, 500);


// The code below should automatically run on https://eve-gatecheck.space/eve
var auth = "";
function setFirstWaypoint(sysid){
fetch("https://esi.evetech.net/latest/ui/autopilot/waypoint/?add_to_beginning=false&clear_other_waypoints=true&destination_id="+sysid, {
  "headers": {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9,sv;q=0.8",
    "authorization": auth,
    "content-type": "application/json",
    "sec-ch-ua": "\"Microsoft Edge\";v=\"95\", \"Chromium\";v=\"95\", \";Not A Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site"
  },
  "referrer": "https://eveeye.com/",
  "referrerPolicy": "strict-origin-when-cross-origin",
  "body": null,
  "method": "POST",
  "mode": "cors",
});
}

function setWaypoint(i){
    fetch("https://esi.evetech.net/latest/ui/autopilot/waypoint/?add_to_beginning=false&clear_other_waypoints=false&destination_id="+sysids[i], {
        "headers": {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9,sv;q=0.8",
            "authorization": auth,
            "content-type": "application/json",
            "sec-ch-ua": "\"Microsoft Edge\";v=\"95\", \"Chromium\";v=\"95\", \";Not A Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site"
        },
        "referrer": "https://eveeye.com/",
        "referrerPolicy": "strict-origin-when-cross-origin",
        "body": null,
        "method": "POST",
        "mode": "cors",
    }).then(res => {
        if(i == sysids.length-1)
            return;
        setWaypoint(++i);

    });
}
    var j = 1
    var sysids = []
    function setAllWaypoints(){
        var jumpSystems = document.querySelector("#result > table > tbody").getElementsByTagName('tr');
        sysids = []
        j = 1;
        for(var i=0;i<jumpSystems.length;i++){
            sysids.push(jumpSystems[i].getElementsByTagName('td')[5].getElementsByTagName('a')[0].href.replace('https://zkillboard.com/system/','').replace('/',''));
        }
        setFirstWaypoint(sysids[0]);
        setWaypoint(j);

    }

    let btn = document.createElement("button");
    btn.innerHTML = "Set Destination";
    btn.style.padding= '5px 10px 5px 10px';
    btn.style.borderRadius= '5px';
    btn.style.cursor= 'pointer';
    btn.style.fontWeight= '700';
    btn.onclick = function () {
        setAllWaypoints();
    };
    document.querySelector("#main > p").appendChild(btn);

    let btn3 = document.createElement("button");
       btn3.style.padding= '5px 10px 5px 10px';
    btn3.style.borderRadius= '5px';
    btn3.style.cursor= 'pointer';
    btn3.style.fontWeight= '700';
    btn3.innerHTML = "Auth";
    btn3.onclick = async function () {
        var ww = window.open('https://eveeye.com/', '');
        setTimeout(async () => {
            auth = await navigator.clipboard.readText();
            if(auth.includes("Bearer"))
                displayAuth.innerText = "Authorized";
            else
                displayAuth.innerText = "Failed Auth";
        },2950);

    };
    document.querySelector("#main > p").appendChild(btn3);

    let displayAuth = document.createElement("p");
    displayAuth.innerText = "No Auth";
    document.querySelector("#main > p").appendChild(displayAuth);