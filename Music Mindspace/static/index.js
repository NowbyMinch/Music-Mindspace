let edit_pop2 = document.getElementById('edit-pop2')
let pop2 = document.getElementById('pop2')
let save = document.getElementById('save');
let edit_title = document.getElementById('edit-title');
let edit_description = document.getElementById('edit-description');
let title = document.getElementById('title');
let edit_icon = document.getElementById('edit-icon')
let pop = document.getElementById('pop')
let edit_pop = document.getElementById('edit-pop')
let close_icon = document.getElementById('close-icon');
let description = document.getElementById('description');
let edit_title2 = document.getElementById('edit-title2');
let edit_description2 = document.getElementById('edit-description2');
const body = document.body;
let main = document.querySelector('.main');

let maximum = document.getElementById('maximum')
let maximum2 = document.getElementById('maximum2')

let main_container = document.getElementById('main_container')
let add_song = document.getElementById('add');
let close_icon2 = document.getElementById('close-icon2');

document.addEventListener('DOMContentLoaded', () => {
    
    add_song.addEventListener('click', function(){
        edit_pop2.style.display = 'flex'
        pop2.style.display = 'flex'
    });
    
    edit_title2.addEventListener('input', function(){
        if (edit_title2.value.length > 43){
            maximum.style.display = 'block';
        }
        else{
            maximum.style.display = 'none';
        }
        
    });

    edit_description2.addEventListener('input', function(){
        if (edit_description2.value.length > 10){
            maximum2.style.display = 'block';
        }
        else{
            maximum2.style.display = 'none';
        }
        
    });

    close_icon2.addEventListener('click', function(){
        edit_pop2.style.display = 'none'
        pop2.style.display = 'none'
        maximum.style.display = 'none';
        maximum2.style.display = 'none';
        edit_title.value = ''
        edit_description.value = ''
    });


    edit_icon.addEventListener('click', function(){
        pop.style.display = 'flex'
        edit_pop.style.display = 'flex'
    });
    
    edit_description.addEventListener('input', function(){
        if (edit_description.value.length > 609){
            maximum2.style.display = 'block';
        }
        else{
            maximum2.style.display = 'none';
        }
        
    });
    
    edit_title.addEventListener('input', function(){
        if (edit_title.value.length > 43){
            maximum.style.display = 'block';
        }
        else{
            maximum.style.display = 'none';
        }
        
    });
    
    close_icon.addEventListener('click', function(){
        edit_pop.style.display = 'none'
        pop.style.display = 'none'
        maximum.style.display = 'none';
        maximum2.style.display = 'none';
        edit_title.value = ''
        edit_description.value = ''
    });
    
    save.addEventListener('click', function(){
        if (edit_title.value.trim() !== ""){
            if (edit_title.value.length < 43){
                title.innerText = edit_title.value;
            }
        }

        if (edit_description.value.trim() !== ""){
            if (edit_description.value.length < 609){
                description.innerText = edit_description.value;
            }
        }
        
        if (edit_title.value.trim() !== "" || edit_description.value.trim() !== ""){
            edit_pop.style.display = 'none'
            pop.style.display = 'none'
            body.style.overflow = 'auto'

        }      
    }); 
});