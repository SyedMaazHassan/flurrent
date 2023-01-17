function openNav() {
    document.getElementById("mySidenav").style.width = "520px";
    // $("#mySidenav").css('box-shadow', '10px 10px 10px 15px #cccccc');
    $("#overlay").show();
    $("#notification-qty").css("opacity", "0");
    $("#notification-qty").text("0");

  }
  
  function closeNav() {
    console.log("closed clicked");
    document.getElementById("mySidenav").style.width = "0";
    $("#overlay").hide();
    // $("#mySidenav").css('box-shadow', 'none');
  }
  
  $("#overlay").on("click", function (e) {
    closeNav();
  });
  
  $(document).on("keyup", function (e) {
    if (e.key === "Escape") {
      closeNav();
    }
  });