const RES_NEGATIVE = 'RES_NEGATIVE';
const RES_FINE = 'RES_FINE';
const RES_BETTER = 'RES_BETTER';
const RES_WOW = 'RES_WOW';
const RES_SAVE = 'RES_SAVE';
const ALL_RESPONSES = [RES_NEGATIVE, RES_FINE, RES_BETTER, RES_WOW, RES_SAVE];

const DISPLAY = {
  RES_NEGATIVE: ['(N)egative', 'I wish to see no more of this'], 
  RES_FINE: ['(O)k', 'I feel neutral'], 
  RES_BETTER: ['(H)as Value', 'I can enjoy it'],
  RES_WOW: ['(G)ood', 'One of the rare good ones'], 
  RES_SAVE: ['(S)tar', 'Super good. Save to disk'], 
}

const WAITING = 'WAITING';
const EVALING = 'EAVLING';

let stage = WAITING;
const globalObj = {
  doc_id: null, 
}

window.onload = () => {
  const buttonDiv = document.getElementById('buttondiv');
  for (const response of ALL_RESPONSES) {
    const b = document.createElement('button');
    b.innerHTML = DISPLAY[response][0];
    b.setAttribute('title', DISPLAY[response][1]);
    b.addEventListener('click', onClick.bind(null, response));
    buttonDiv.appendChild(b);
  }
  askNew();
};

const askNew = () => {
  const xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = () => {
    if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
      const { doc_id, mode } = JSON.parse(xmlHttp.responseText);
      globalObj.doc_id = doc_id;
      const imgDiv = document.getElementById('imgdiv');
      imgDiv.innerHTML = '';
      const img = document.createElement('img');
      img.src = `img?doc_id=${doc_id}`;
      imgDiv.appendChild(img);
      stage = EVAL;

      const h2 = getElementById('h2');
      h2.innerHTML = `${mode} Mode`;
    }
  }
  xmlHttp.open("GET", `next?rand=${Math.random()}`, true);
  xmlHttp.send(null);
};

const onClick = (response) => {
  if (stage !== EVALING) {
    alert('Too soon.');
    return;
  }
  const xmlHttp = new XMLHttpRequest();
  xmlHttp.onreadystatechange = () => {
    if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
      // console.log(xmlHttp.responseText);
      stage = WAITING;
      askNew();
    }
  }
  xmlHttp.open(
    "GET", `response?doc_id=${
      globalObj.doc_id
    }&response=${response}`, true, 
  );
  xmlHttp.send(null);
};
