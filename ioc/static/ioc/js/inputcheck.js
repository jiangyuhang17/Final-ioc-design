function datecheck (year,month) {
    var y = Number(year);
    var m = Number(month);
    var date = new Date();
    datey = date.getFullYear();
    datem = date.getMonth();
    if(isNaN(y)){
        return 1;
    }
    if(isNaN(m))
        return 2;
    if(y>datey||y<1000)
        return 3;
    if((y==datey&&m>datem)||m<=0||m>12)
        return 4;
    return 0;
}

function phonecheck(phone) {
      var myreg=/^[1][0-9]{10}$/;
      if (!myreg.test(phone)) {
          return 1;
      } else {
          return 0;
      }
  }