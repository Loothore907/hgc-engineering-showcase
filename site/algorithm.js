/* New illustrative implementation; synthetic unitless nodes only. */
(function (root) {
  "use strict";
  const fixture = [[85,88],[89,76],[65,45],[16,15],[44,57],[80,90],[90,83],[45,84]]
    .map(([x,y],i)=>({id:String.fromCharCode(65+i),x,y}));
  const distance=(a,b)=>Math.hypot(a.x-b.x,a.y-b.y);
  const cost=route=>route.reduce((sum,p,i)=>sum+distance(p,route[(i+1)%route.length]),0);
  function nearest(points) {
    const origin=points.find(p=>p.id==="A");
    if(!origin) throw new Error("Fixture origin A is required");
    const remaining=points.filter(p=>p.id!=="A").slice().sort((a,b)=>a.id.localeCompare(b.id));
    const route=[origin];
    while(remaining.length) {
      const current=route[route.length-1];
      remaining.sort((a,b)=>distance(current,a)-distance(current,b)||a.id.localeCompare(b.id));
      route.push(remaining.shift());
    }
    return route;
  }
  function improve(route) {
    let best=route.slice(), bestCost=cost(best), changed=true;
    while(changed) {
      changed=false;
      outer: for(let start=1;start<best.length-1;start++) {
        for(let end=start+1;end<best.length;end++) {
          const candidate=best.slice(0,start).concat(best.slice(start,end+1).reverse(),best.slice(end+1));
          const nextCost=cost(candidate);
          if(nextCost+0.001<bestCost) { best=candidate; bestCost=nextCost; changed=true; break outer; }
        }
      }
    }
    return best;
  }
  const api={fixture,distance,cost,nearest,improve};
  if(typeof module!=="undefined") module.exports=api;
  root.HGCAlgorithms=api;
})(typeof globalThis!=="undefined"?globalThis:this);

