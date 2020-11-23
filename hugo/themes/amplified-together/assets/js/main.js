(function($) { // Begin jQuery
    $(function() { // DOM ready
      // If a link has a dropdown, add sub menu toggle.
      $('nav ul li a:not(:only-child)').click(function(e) {
        $(this).siblings('.nav-dropdown').toggle();
        // Close one dropdown when selecting another
        $('.nav-dropdown').not($(this).siblings()).hide();
        e.stopPropagation();
      });
      // Clicking away from dropdown will remove the dropdown class
      $('html').click(function() {
        $('.nav-dropdown').hide();
      });
      // Toggle open and close nav styles on click
      $('#nav-toggle').click(function() {
        $('nav ul').slideToggle();
      });
      // Hamburger to X toggle
      $('#nav-toggle').on('click', function() {
        this.classList.toggle('active');
      });

      // Builds the fave data for an element
      function buildFave($ele) {
        return {
          studentname: $ele.attr('data-studentname').trim(),
          img: $ele.attr('data-img').trim(),
          url: $ele.attr('data-url').trim()
        }
      }

      // Does the actual check against localstorage
      function isFaved(f) {
        var faves = (localStorage.getItem('faves')) 
          ? JSON.parse(localStorage.getItem('faves'))
          : []
        for (fave of faves) {
          if (fave.studentname == f.studentname) {
            return true
          }
        }
        return false
      }

      // Add class to already faved
      $('.add-favorite').each(function() {
        var fave = buildFave($(this))
        if (isFaved(fave)) {
          $(this).addClass('faved')
        }
      })

      // Add to favorites
      $('.add-favorite').click(function(e) {
        var faves = (localStorage.getItem('faves')) 
          ? JSON.parse(localStorage.getItem('faves'))
          : []
        var fave = buildFave($(this))
        if (!isFaved(fave)) {
          faves.push(fave)
          localStorage.setItem('faves', JSON.stringify(faves))
          console.log(fave.studentname, "ADDED to faves")
        } else {
          console.log(fave.studentname, "is already a fave")
        }
      })

      // Show favorites!
      $('#favorites-listing').each(function() {
        var faves = (localStorage.getItem('faves')) 
          ? JSON.parse(localStorage.getItem('faves'))
          : []
        for (fave of faves) {
          $h3 = $('<h3></h3>')
          $student = $('<div class="student preview"></div>')
          $imgdiv = $('<div class="image"></div>')
          $img = $('<img src="' + fave.img + '">')
          $name = $('<a href="' + fave.url + '">' + fave.studentname + '</a>')
          $img.appendTo($imgdiv)
          $imgdiv.appendTo($student)
          $name.appendTo($student)
          $student.appendTo($h3)
          $h3.appendTo($(this))
        }
      })
    }); // end DOM ready
  })(jQuery); // end jQuery