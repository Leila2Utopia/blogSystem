// 点赞踩灭事件
$(".action").click(function () {
    if ($(".info").attr("username")){
        var is_up;
        is_up=$(this).hasClass("diggit");
        article_id=$(".info").attr("article_id");

        $.ajax({
            url:"blog/digg/",
            type:"post",
            data:{
                is_up:is_up,
                article_id:article_id,
                csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val()
            },
            success:function (data) {
                console.log(data);
                // 点赞踩灭成功
                if (data.state){
                    // 点赞
                    if(is_up){
                        var val=$("#digg_count").text();
                        val=parseInt(val)+1;
                        $("#digg_count").text(val);
                    }
                    // 踩灭
                    else{
                        var val=$("#bury_count").text();
                        val=parseInt(val)+1;
                        $("#bury_count").text(val);
                    }
                }
                // 点赞踩灭失败 重复提交
                else{
                    if (data.first_action){
                         $("#digg_tips").html("您已推荐过了");
                        setTimeout(function () {
                            $("#digg_tips").html("");
                        },1000)
                    }
                    else{
                        $("#digg_tips").html("您已反对过了");
                        setTimeout(function () {
                            $("#digg_tips_").html("");
                        },1000)
                    }
                }
            }
        })
    }
    else{
        var s="<a href='/login/' class='pull-right'>请登录！</a>";
        $("#div_digg").after(s);
    }
});



// 评论相关
// 获取评论信息
// $.ajax({
//     url:"/blog/comment_tree/"+$(".info").attr("article_id"),
//     success:function (comment_list) {
//         console.log(comment_list);
//
//         html="";
//         $.each(comment_list,function (index,comment_dict) {
//             temp='<div comment_tree_id='+comment_dict.pk+' class="comment_item"> <span class="content">'+comment_dict.content+'</span></div>'
//
//             if(!comment_dict.parent_comment_id){
//                 $(".comment_tree").append(temp)
//             }
//             else{
//                 pid=comment_dict.parent_comment_id;
//                 $("[comment_tree_id='+pid+']").append(temp)
//             }
//         });
//     }
// });
// 提交评论事件
var pid="";
$(".comment_btn").click(function () {
   article_id=$(".info").attr("article_id");
   content=$("#comment_content").val();

   // 处理content
   if(pid){
       var index=content.indexOf("\n");
       content=content.slice(index+1)
   }

   $.ajax({
       url:"/blog/comment/",
       type:"post",
       data:{
           article_id:article_id,
           content:content,
           pid:pid,
           csrfmiddlewaretoken: $("[name='csrfmiddlewaretoken']").val()
       },
       success:function (data) {
           console.log(data);
           ctime=data.ctime;
           content=data.content;
           username=$(".info").attr("username");
           s = '<li class="comment_item list-group-item temp"> <div> <span>' + ctime + '</span>&nbsp;&nbsp;<span>' + username + '</span> </div> <div class="comment_con"><p>' + content + '</p></div> </li>'

           $(".comment_list").append(s);

           $(".comment_content").val("");

           pid="";
       }

   })
});

// 回复事件
$(".reply_btn").click(function () {
    $("#comment_content").focus();

    var val="@"+$(this).attr("username")+"\n";
    $("#comment_content").val(val);

    pid=$(this).attr("comment_id")
});