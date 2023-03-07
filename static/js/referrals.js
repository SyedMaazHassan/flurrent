copyText = async (link) => {
  try {
    await navigator.clipboard.writeText(link)
    const success_alert__container = document.getElementById("success_alert__container")
    success_alert__container.classList.remove("d-none")
    success_alert__container.classList.add("d-block")
    setTimeout(() => {
      success_alert__container.classList.remove("d-block")
      success_alert__container.classList.add("d-none")
    }, 3000)
  } catch (err) {
    console.log(err)
  }
}
