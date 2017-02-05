	var winW=$(window).width();
	var winH=$(window).height();
	var Ratio=winW/winH;

  //div設定
	 $("#gallery").css("top",0)
			   .height(winH)
			   .width(winW)
			   .css("left","50%")
			   .css("margin-left",-1*winW/2)				   
	 ;	
	 
	$(window).resize(function() {
	  $("#gallery").height($(window).height())
			    .width($(window).height()*Ratio)
			    .css("left","50%")
			    .css("margin-left",-1*$("#gallery").width()/2)					
			    ;
	});	 

  //global變數------------------------------------------		 
	  var FV=75;//field of view;
	  var myW=$("#gallery").width();
	  var myH=$("#gallery").height();
	  
	  var ASPECT=myW/myH;//window.innerWidth / window.innerHeight;
	  var Near=0.1;
	  var Far=1000;
	  var controls;
	  var light;
	  var planeARR=[];
	  var textureARR=[];
	  var to_load=[];
	  var mode="grid";
	  var gapD=10;
	  var gapZ=10
	  var oX=gapD*(-4);
	  var oY=gapD*(4);
	  var oZ=0;	  
	  var logoW=$("#logoimg").width();
	  var infoJSON;
	  var nowWatch="intro";
	  //var helixN=36;//一圈個數
	  //var helixR=30;
	  //var helixA=2*Math.PI/helixN;
	  //var helixD=10/36;//上升高度	  
	  
  //基本設定------------------------------------------		
  var scene = new THREE.Scene();

  var camera = new THREE.PerspectiveCamera(FV,ASPECT,Near,Far);
	  camera.position.set(0, 0, 60); 	  
	  //camera.position.z = 5;
	  //camera.up = new THREE.Vector3(0,0,1);//與視軸正交的up軸，會被TracjkBall控制
	  //camera.lookAt(new THREE.Vector3(0,0,0)); //會被TracjkBall控制，要改control.target
	  //scene.add(camera);//trackball自動設定
	  
  var renderer = new THREE.WebGLRenderer({ antialias: true,alpha: true });	  //alpha改成透明
	  renderer.setSize(myW,myH);//renderer.setSize( window.innerWidth, window.innerHeight );
 
      renderer.shadowMapEnabled = true;
	  renderer.shadowMapSoft = true;

	  renderer.shadowCameraNear = 3;
	  renderer.shadowCameraFar = camera.far;
	  renderer.shadowCameraFov = 50;

	  renderer.shadowMapBias = 0.0039;
	  renderer.shadowMapDarkness = 0.5;
	  renderer.shadowMapWidth = 1024;
	  renderer.shadowMapHeight = 1024;				
	  
  var DIV=$("#gallery");
	  DIV.append(renderer.domElement);	
	  $(window).resize(function(){
			renderer.setSize( $(window).height()*Ratio, $(window).height());//要重新render Size
			
		});	 	  
	  //document.body.appendChild (renderer.domElement);   
	  //document.getElementById("A").appendChild(renderer.domElement);  
	  //$('body').append(renderer.domElement);		
  //基本設定end------------------------------------------	
  
	
		//load的東西要用FF試，Chrome無法本機load
		var imgN=515;//圖片總數2017/0205
		var loadedN=0;
		var path="work/"
		
		for(var i=0;i<imgN;i++){
			//jpg陣列
			to_load.push(path+(i+1)+".jpg");
			//planeARR.push("");			
		};
	
		var logoIMG=$("#logoimg");	
		TweenMax.to(logoIMG, 2,{scale:0.5,ease:Linear.easeOut,yoyo:true,repeat:-1});	
		//TweenMax.to(logoIMG, 10,{height:0,ease:Linear.easeOut,yoyo:true});
		
		//最重要的載圖
		for(var j=0;j<imgN;j++){	
		
				
			textureARR.push(new THREE.ImageUtils.loadTexture(to_load[j],{},function(texture){ 
							loadedN+=1;	//計數load總數	
		
							//
							var textN=textureARR.indexOf(texture);					
							var geometry = new THREE.PlaneGeometry(5,5,1,1);
							var material = new THREE.MeshBasicMaterial({
												//color: 0xff0000, 
												wireframe: false,
												side: THREE.DoubleSide, 
												map:texture
												});
							planeARR[textN]=new THREE.Mesh( geometry, material );	
							scene.add( planeARR[textN] );	
												
							  //load完才render
							  if(loadedN==imgN){ 
							  		
								TweenMax.to($("#BG"), 3,{opacity:0,ease:Linear.easeOut,onComplete:function(){
											//TweenMax.to($("#BG"), 3,{opacity:0,ease:Linear.easeOut,onComplete:function(){
												$("#BG").remove();
											//}});										
										}});//to		
										
									  planeDOT();//布置位置
									  planeDOT2();//布置位置
									  myControl();									  
									  render();	
									  info();//讀圖說									  
									  preface();
									  music();
									  starForge();
								};//if	
						}));//push
		
			
		};//for	
		
		

	  //===========================================================	
			function music(){
				$("body").append("<audio title='Music: http://www.bensound.com' style='z-index:99000;position:fixed;bottom:1px;right:1px' autoplay='autoplay' loop='loop' controls='controls'><source src='bensound-betterdays.mp3' type='audio/mpeg'></audio>");
				
				
			};
	  
	      function info(){
			  
			$.getJSON( "info.json", function( data ) {
					//注意json檔，最後不能有逗號，否則讀取失敗;
					//json的key,val全為str
					infoJSON=data;							 			  
			  $("#infocontent").html(infoJSON["intro"]);
					window.setInterval(function(){
						  var introN=0;	
						  for(var k=0;k<imgN;k++){
							  
							  var dX=camera.position.x-planeARR[k].position.x;
							  var dY=camera.position.y-planeARR[k].position.y;
							  var dZ=camera.position.z-planeARR[k].position.z;
							  var watchD=Math.sqrt(dX*dX+dY*dY+dZ*dZ);
							  
							  if(watchD<5){	
									if(nowWatch!==(k+1)+""){
										nowWatch=(k+1)+"";
																			
										var tmpTXT=infoJSON[nowWatch];
										var tmpR=/【.+】/gi;
										var tmpTitle=tmpTXT.match(tmpR);
										$("#infotitle").text(tmpTitle);
										
										break;//  										
									};

							  }else{
								  introN+=1;
								  if(introN==imgN){ 
									nowWatch="intro"; 
									$("#infotitle").text("說明");
								  
								  };
							       //nowWatch="intro" ; //不可每張intro，要等全部確定都沒有才intro，否則說明內容會跳動	
							  };
							  
						  };//for
							//$("#infotitle").text(nowWatch);
						}, 400);//setinterval
						
			 var infobox=$("#infobox");			 
			 infobox.hover(
						  function() {
							TweenMax.to(infobox, 0.2,{bottom:"-30px",ease:Power3.easeInOut});					
									
							if($("#infocontent").attr("data-now")!==nowWatch){
								var tmpTXT=infoJSON[nowWatch];
								tmpTXT=tmpTXT.replace(/【.+】/gi,"");
								$("#infocontent").html(tmpTXT)
												 .attr("data-now",nowWatch)
												 .scrollTop(0)
												;									
							};//if									
													
						  }, 
						  function() {
							TweenMax.to(infobox, 0.2,{bottom:"-275px",ease:Power3.easeInOut});	

						  }
						)//hover
						;

			});//getjson
			  
		  };//info
	  
	  
	  
	  
		  function preface(){
			  var myPre=$("#preface");
			  
			  myPre
				.click(function(){
					var URL="https://www.instagram.com/feynmanpan/";
					window.open(URL,'_blank');
					
				});//click
			  
		  };//preface
		

		 	

		
		  function planeDOT(){
		    var domEvents	= new THREEx.DomEvents(camera, renderer.domElement);//一定要這行

			for(var k=0;k<imgN;k++){
				//排列位置___________________________________
				var zN=Math.floor((k+1)/81)-(1-(Math.ceil((k+1)/81)-Math.floor((k+1)/81)));//from 0
				var newk=(k+1)-zN*81;
			    var yN=Math.floor(newk/9)-(1-(Math.ceil(newk/9)-Math.floor(newk/9)));//from 0
				var xN=newk-1-yN*9;//from 0
					
				planeARR[k].position.x=oX+xN*gapD;
				planeARR[k].position.y=oY-yN*gapD;
				planeARR[k].position.z=oZ-zN*gapZ;
		

				//互動___________________________________	
				planeARR[k].material.transparent=true;//要true，opacity才不會奇怪現象	
				//over	
				domEvents.addEventListener(planeARR[k], 'mouseover', function(e){
    				  $("#gallery").css("cursor","pointer");
					  //不能用k，事件發生時的k與定義時已不同
					  var _this=e.target;			
						TweenMax.to(_this.material, 0.1,{opacity:0.6,ease:Linear.easeOut});					  
						TweenMax.to(_this.material, 0.1,{delay:0.1,opacity:1,ease:Linear.easeOut});	
						
					}, false);//
				//out
				domEvents.addEventListener(planeARR[k], 'mouseout', function(e){
    				  $("#gallery").css("cursor","default");
					  var _this=e.target;
					  //_this.material.opacity=1;
					}, false);//					
				//點擊觀看
				domEvents.addEventListener(planeARR[k], 'click', function(e){
    				  var _this=e.target;
					  var _thisX=_this.position.x;
					  var _thisY=_this.position.y;
					  var _thisZ=_this.position.z;
					  var _thisRY=_this.rotation.y;
					  var _thisRX=_this.rotation.x;
						
						 //矯正up軸
						 TweenMax.to(camera.up,1,{x:0,ease:Linear.easeInOut});
						 TweenMax.to(camera.up,1,{y:1,ease:Linear.easeInOut});
						 TweenMax.to(camera.up,1,{z:0,ease:Linear.easeInOut});
						 //定位及轉向
						 var A=[_thisX,_thisY,_thisZ,_thisRX-_thisRY]//A[3]相當於helix的theta
						 var B=4.5;//與畫距離						 
						 TweenMax.to(camera.position,1,{x:A[0]+B*Math.sin(A[3]),ease:Power3.easeInOut});
						 TweenMax.to(camera.position,1,{y:A[1],ease:Power3.easeInOut});
						 TweenMax.to(camera.position,1,{z:A[2]+B*Math.cos(A[3]),ease:Power3.easeInOut});						 
						 //看畫中心
						 TweenMax.to(controls.target,1,{x:A[0],ease:Power3.easeInOut});
						 TweenMax.to(controls.target,1,{y:A[1],ease:Power3.easeInOut});
						 TweenMax.to(controls.target,1,{z:A[2],ease:Power3.easeInOut,onComplete:controlNEW1});					
						 
						 
						 function controlNEW1(){
							//myControl(new THREE.Vector3(A[0],A[1],A[2]));   //新版trackball好像不必重新對target
						 };//					  
								  
					  
					}, false);//							
					
			};//for
		  
		  };//DOT 	


		  function planeDOT2(){ 
			 var gridBTN=$("#grid");
			 var surfaceBTN=$("#surface");			 
			 var lineBTN=$("#line");
			 var helixBTN=$("#helix");
			 var helix2BTN=$("#helix2");
			 //格狀排列__________________________________________________
			 gridBTN.click(function(){
				if(mode!=="grid"){ 
					mode="grid";
					 //矯正up軸
					 TweenMax.to(camera.up,1,{x:0,ease:Power3.easeInOut});
					 TweenMax.to(camera.up,1,{y:1,ease:Power3.easeInOut});
					 TweenMax.to(camera.up,1,{z:0,ease:Power3.easeInOut});								
					 //離畫中心一段距離
					 TweenMax.to(camera.position,3,{x:0,ease:Power3.easeInOut});
					 TweenMax.to(camera.position,3,{y:0,ease:Power3.easeInOut});
					 TweenMax.to(camera.position,3,{z:60,ease:Power3.easeInOut});
					 //看畫中心
					 TweenMax.to(controls.target,1,{x:0,ease:Power3.easeInOut});
					 TweenMax.to(controls.target,1,{y:0,ease:Power3.easeInOut});
					 TweenMax.to(controls.target,1,{z:0,ease:Power3.easeInOut});					
					for(var k=0;k<imgN;k++){
								//排列位置___________________________________
								var zN=Math.floor((k+1)/81)-(1-(Math.ceil((k+1)/81)-Math.floor((k+1)/81)));//from 0
								var newk=(k+1)-zN*81;
								var yN=Math.floor(newk/9)-(1-(Math.ceil(newk/9)-Math.floor(newk/9)));//from 0
								var xN=newk-1-yN*9;//from 0
									
								TweenMax.to(planeARR[k].position, 1.5+(k/imgN),{x:oX+xN*gapD,ease:Power4.easeInOut});
								TweenMax.to(planeARR[k].position, 1.5+(k/imgN),{y:oY-yN*gapD,ease:Power4.easeInOut});
								TweenMax.to(planeARR[k].position, 1.5+(k/imgN),{z:oZ-zN*gapZ,ease:Power4.easeInOut});
								
								//先喬ry，因為helix會使y多轉，先轉成跟rx rz一樣
								//xyz一直轉一樣角度，才會正面
								TweenMax.to(planeARR[k].rotation, 0.5,{y:planeARR[k].rotation.x,ease:Power4.easeInOut});
								//mode中途切換時，強迫轉到整數pi
								var rX=Math.floor(planeARR[k].rotation.x/Math.PI)*Math.PI+1*Math.PI;
								if(rX==planeARR[k].rotation.x){
									rX=planeARR[k].rotation.x+Math.PI;
								}; //會有一樣的奇怪現象，強迫加pi
								
							
													
							TweenMax.to(planeARR[k].rotation, 1+(k/imgN),{delay:0.6,x:rX,ease:Power4.easeInOut});
							TweenMax.to(planeARR[k].rotation, 1+(k/imgN),{delay:0.6,y:rX,ease:Power4.easeInOut});
							TweenMax.to(planeARR[k].rotation, 1+(k/imgN),{delay:0.6,z:rX,ease:Power4.easeInOut,onComplete:controlNEW1});
																		
															 
									 function controlNEW1(){
										//myControl();   //新版trackball好像不必重新對target
										
									 };//									
								  
						};//for					
				
				};//if			 
			 });//click

			 //平面排列____________________________________________________
			 surfaceBTN.click(function(){
				if(mode!=="surface"){
					mode="surface";
					 //矯正up軸
					 TweenMax.to(camera.up,1,{x:0,ease:Power3.easeInOut});
					 TweenMax.to(camera.up,1,{y:1,ease:Power3.easeInOut});
					 TweenMax.to(camera.up,1,{z:0,ease:Power3.easeInOut});								
					 //離畫中心一段距離
					 TweenMax.to(camera.position,3,{x:0,ease:Power3.easeInOut});
					 TweenMax.to(camera.position,3,{y:0,ease:Power3.easeInOut});
					 TweenMax.to(camera.position,3,{z:60,ease:Power3.easeInOut});
					 //看原點
					 TweenMax.to(controls.target,1,{x:0,ease:Power3.easeInOut});
					 TweenMax.to(controls.target,1,{y:0,ease:Power3.easeInOut});
					 TweenMax.to(controls.target,1,{z:0,ease:Power3.easeInOut});	
                      
                     //
					  var edgeN=Math.ceil(Math.sqrt(imgN));
					  var pX=(-5)*edgeN/2-2.5;
					  var pY=-1*pX;
					  var pZ=0;	  					 
					for(var k=0;k<imgN;k++){
								//排列位置___________________________________	
								var yN=Math.floor((k+1)/edgeN)-(1-(Math.ceil((k+1)/edgeN)-Math.floor((k+1)/edgeN)));//from 0
								var xN=k-yN*edgeN;//from 0								
									
								TweenMax.to(planeARR[k].position, 1.5+(k/imgN),{x:pX+5*xN,ease:Power4.easeInOut});
								TweenMax.to(planeARR[k].position, 1.5+(k/imgN),{y:pY-5*yN,ease:Power4.easeInOut});
								TweenMax.to(planeARR[k].position, 1.5+(k/imgN),{z:0,ease:Power4.easeInOut});
								
								//先喬ry，因為helix會使y多轉，先轉成跟rx rz一樣
								//xyz一直轉一樣角度，才會正面
								TweenMax.to(planeARR[k].rotation, 0.5,{y:planeARR[k].rotation.x,ease:Power4.easeInOut});
								//mode中途切換時，強迫轉到整數
								var rX=Math.floor(planeARR[k].rotation.x/Math.PI)*Math.PI+Math.PI;							
								if(rX==planeARR[k].rotation.x){
									rX=planeARR[k].rotation.x+Math.PI;
								}; //會有一樣的奇怪現象
								
								TweenMax.to(planeARR[k].rotation, 1+(k/imgN),{delay:0.6,x:rX,ease:Power4.easeInOut});
								TweenMax.to(planeARR[k].rotation, 1+(k/imgN),{delay:0.6,y:rX,ease:Power4.easeInOut});
								TweenMax.to(planeARR[k].rotation, 1+(k/imgN),{delay:0.6,z:rX,ease:Power4.easeInOut,onComplete:controlNEW1});											 
					
									 function controlNEW1(){
										//myControl();   //新版trackball好像不必重新對target
									 };//	
									 
																								
						};//for					
				
				};//if			 
			 });//click	

			 
			 //直線排列____________________________________________________
			 lineBTN.click(function(){
				if(mode!=="line"){
					mode="line";
					 //矯正up軸
					 TweenMax.to(camera.up,1,{x:0,ease:Power3.easeInOut});
					 TweenMax.to(camera.up,1,{y:1,ease:Power3.easeInOut});
					 TweenMax.to(camera.up,1,{z:0,ease:Power3.easeInOut});								
					 //離畫中心一段距離
					 TweenMax.to(camera.position,3,{x:0,ease:Power3.easeInOut});
					 TweenMax.to(camera.position,3,{y:0,ease:Power3.easeInOut});
					 TweenMax.to(camera.position,3,{z:60,ease:Power3.easeInOut});
					 //看原點
					 TweenMax.to(controls.target,1,{x:0,ease:Power3.easeInOut});
					 TweenMax.to(controls.target,1,{y:0,ease:Power3.easeInOut});
					 TweenMax.to(controls.target,1,{z:0,ease:Power3.easeInOut});					
					for(var k=0;k<imgN;k++){
								//排列位置___________________________________									
								TweenMax.to(planeARR[k].position, 1.5+(k/imgN),{x:k*(gapD-4.5),ease:Power4.easeInOut});
								TweenMax.to(planeARR[k].position, 1.5+(k/imgN),{y:0,ease:Power4.easeInOut});
								TweenMax.to(planeARR[k].position, 1.5+(k/imgN),{z:0,ease:Power4.easeInOut});
								
								//先喬ry，因為helix會使y多轉，先轉成跟rx rz一樣
								//xyz一直轉一樣角度，才會正面
								TweenMax.to(planeARR[k].rotation, 0.5,{y:planeARR[k].rotation.x,ease:Power4.easeInOut});
								//mode中途切換時，強迫轉到整數
								var rX=Math.floor(planeARR[k].rotation.x/Math.PI)*Math.PI+Math.PI;						
								if(rX==planeARR[k].rotation.x){
									rX=planeARR[k].rotation.x+Math.PI;
								}; //會有一樣的奇怪現象								
													
								TweenMax.to(planeARR[k].rotation, 1+(k/imgN),{delay:0.6,x:rX,ease:Power4.easeInOut});
								TweenMax.to(planeARR[k].rotation, 1+(k/imgN),{delay:0.6,y:rX,ease:Power4.easeInOut});
								TweenMax.to(planeARR[k].rotation, 1+(k/imgN),{delay:0.6,z:rX,ease:Power4.easeInOut,onComplete:controlNEW1});											 
					
									 function controlNEW1(){
										//myControl();   //新版trackball好像不必重新對target
									 };//	
									 
																								
						};//for					
				
				};//if			 
			 });//click		

			 //helix排列____________________________________________________
			 helixBTN.click(function(){
				if(mode!=="helix"){
					mode="helix";
					 //矯正up軸
					 TweenMax.to(camera.up,1,{x:0,ease:Power3.easeInOut});
					 TweenMax.to(camera.up,1,{y:1,ease:Power3.easeInOut});
					 TweenMax.to(camera.up,1,{z:0,ease:Power3.easeInOut});								
					 //離畫中心一段距離
					 TweenMax.to(camera.position,3,{x:0,ease:Power3.easeInOut});
					 TweenMax.to(camera.position,3,{y:0,ease:Power3.easeInOut});
					 TweenMax.to(camera.position,3,{z:60,ease:Power3.easeInOut});
					 //看原點
					 TweenMax.to(controls.target,1,{x:0,ease:Power3.easeInOut});
					 TweenMax.to(controls.target,1,{y:0,ease:Power3.easeInOut});
					 TweenMax.to(controls.target,1,{z:0,ease:Power3.easeInOut});		
					
					  var helixN=36;//一圈個數
					  var helixR=30;
					  var helixA=2*Math.PI/helixN;
					  var helixD=10/36;//上升高度	  
					 
					for(var k=0;k<imgN;k++){
								//排列位置___________________________________	
								var theta=k*helixA-Math.floor(k*helixA/(2*Math.PI))*2*Math.PI;
								var hX=helixR*Math.sin(theta);
								var hY=k*helixD-40;
								var hZ=helixR*Math.cos(theta)-helixR;								
								
								TweenMax.to(planeARR[k].position, 1.5+(k/imgN),{x:hX,ease:Power4.easeInOut});
								TweenMax.to(planeARR[k].position, 1.5+(k/imgN),{y:hY,ease:Power4.easeInOut});
								TweenMax.to(planeARR[k].position, 1.5+(k/imgN),{z:hZ,ease:Power4.easeInOut});
								
								//mode中途切換時，強迫轉到整數
								var rX=Math.floor(planeARR[k].rotation.x/Math.PI)*Math.PI+Math.PI;
								if(rX==planeARR[k].rotation.x){
									rX=planeARR[k].rotation.x+Math.PI;
								}; //會有一樣的奇怪現象								
								if((rX/Math.PI)%2==0){rX+=Math.PI};//偶數奇數pi，-theta方向不一樣，強迫奇數					
													
								TweenMax.to(planeARR[k].rotation, 1+(k/imgN),{x:rX,ease:Power4.easeInOut});
								TweenMax.to(planeARR[k].rotation, 1+(k/imgN),{y:rX,ease:Power4.easeInOut});
								TweenMax.to(planeARR[k].rotation, 1+(k/imgN),{z:rX,ease:Power4.easeInOut,onComplete:controlNEW1});
								
								//最後rx轉theta								
								TweenMax.to(planeARR[k].rotation, 1,{delay:1+(k/imgN),y:rX-theta,ease:Power4.easeInOut});	
								
									 function controlNEW1(){
										//myControl();   //新版trackball好像不必重新對target
									 };//	
									 
																								
						};//for					
				
				};//if			 
			 });//click					 

			 //helix2排列____________________________________________________
			 helix2BTN.click(function(){
				if(mode!=="helix2"){
					mode="helix2";
					 //矯正up軸
					 TweenMax.to(camera.up,1,{x:0,ease:Power3.easeInOut});
					 TweenMax.to(camera.up,1,{y:1,ease:Power3.easeInOut});
					 TweenMax.to(camera.up,1,{z:0,ease:Power3.easeInOut});								
					 //離畫中心一段距離
					 TweenMax.to(camera.position,3,{x:0,ease:Power3.easeInOut});
					 TweenMax.to(camera.position,3,{y:0,ease:Power3.easeInOut});
					 TweenMax.to(camera.position,3,{z:60,ease:Power3.easeInOut});
					 //看原點
					 TweenMax.to(controls.target,1,{x:0,ease:Power3.easeInOut});
					 TweenMax.to(controls.target,1,{y:0,ease:Power3.easeInOut});
					 TweenMax.to(controls.target,1,{z:0,ease:Power3.easeInOut});		
					
					  var helixN=36;//一圈個數
					  var helixR=40;
					  var helixA=2*Math.PI/helixN;
					  var helixD=10/36;//上升高度	  
					 
					for(var k=0;k<imgN;k++){
								//排列位置___________________________________	
								var theta=k*helixA;
								var hX=helixR*Math.cos(theta);
								var hZ=-1*k*helixD;
								var hY=helixR*Math.sin(theta);								
								
								TweenMax.to(planeARR[k].position, 1.5+(k/imgN),{x:hX,ease:Power4.easeInOut});
								TweenMax.to(planeARR[k].position, 1.5+(k/imgN),{y:hY,ease:Power4.easeInOut});
								TweenMax.to(planeARR[k].position, 1.5+(k/imgN),{z:hZ,ease:Power4.easeInOut});
								
								//先喬ry，因為helix會使y多轉，先轉成跟rx rz一樣
								//xyz一直轉一樣角度，才會正面
								TweenMax.to(planeARR[k].rotation, 0.5,{y:planeARR[k].rotation.x,ease:Power4.easeInOut});
								//mode中途切換時，強迫轉到整數
								var rX=Math.floor(planeARR[k].rotation.x/Math.PI)*Math.PI+Math.PI;
								if(rX==planeARR[k].rotation.x){
									rX=planeARR[k].rotation.x+Math.PI;
								}; //會有一樣的奇怪現象								
								//if((rX/Math.PI)%2==0){rX+=Math.PI};//偶數出問題
								//var rY=Math.floor(planeARR[k].rotation.y/Math.PI)*Math.PI+Math.PI;
								//var rZ=Math.floor(planeARR[k].rotation.z/Math.PI)*Math.PI+Math.PI;
													
								TweenMax.to(planeARR[k].rotation, 1+(k/imgN),{delay:0.6,x:rX,ease:Power4.easeInOut});
								TweenMax.to(planeARR[k].rotation, 1+(k/imgN),{delay:0.6,y:rX,ease:Power4.easeInOut});
								TweenMax.to(planeARR[k].rotation, 1+(k/imgN),{delay:0.6,z:rX,ease:Power4.easeInOut,onComplete:controlNEW1});
								
								//最後rx轉theta
								//TweenMax.to(planeARR[k].rotation, 1,{delay:1+(k/imgN),y:"-="+theta,ease:Power4.easeInOut});	
								
									 function controlNEW1(){
										//myControl();   //新版trackball好像不必重新對target
									 };//	
									 
																								
						};//for					
				
				};//if			 
			 });//click	

			 
		  };//dot2

		  
		  function initLight() {
			var ambientLight = new THREE.AmbientLight(0x222222);
				scene.add(ambientLight);  
			//只有directional跟Spot能投影
			var lightP=2;
			var lightX=10;
			var lightY=27;
			var lightZ=-50;
			light = new THREE.SpotLight(0xFFFFFF,lightP,0);  
			light.position.set(lightX,lightY,lightZ);//.normalize();                       

			light.shadowDarkness = 0.7;
			light.shadowCameraFov = 16;
			light.castShadow = true;	
			//light.shadowCameraVisible = true;	
			/*
			light.shadowCameraNear = 2;	
			light.shadowCameraFar = 115;
			light.shadowCameraLeft = -100;
			light.shadowCameraRight = 100;
			light.shadowCameraTop = 100;
			light.shadowCameraBottom = -100;	
			*/
			scene.add(light);  	            


					//
					//plane.castShadow = true;
					//plane.receiveShadow = true;							
		  };		 
					
					

	
			
		  function myControl(closeUP){   	
			  //限制只在div中感應
			  controls = new THREE.TrackballControls(camera,document.getElementById("gallery"),closeUP);
			  controls.rotateSpeed = 1.0;
			  controls.zoomSpeed = 1.0;
			  controls.panSpeed = 0.8;
			  controls.noZoom = false;
			  controls.noPan = false;
			  controls.staticMoving = false;
			  controls.dynamicDampingFactor = 0.3;
			  controls.keys = [ 0, 0, 0 ];   
		  };//		

		  function render() {		        	
				requestAnimationFrame(render);			
				renderer.render(scene,camera);			
				controls.update();  				
		  };//				  


 function starForge() {
		/* 	Yep, it's a Star Wars: Knights of the Old Republic reference,
			are you really surprised at this point? 
													*/
		var starQty = 45000;
			geometry = new THREE.SphereGeometry(1000, 100, 50);

	    	materialOptions = {
	    		size: 1.0, //I know this is the default, it's for you.  Play with it if you want.
	    		transparency: true, 
	    		opacity: 0.7
	    	};

	    	starStuff = new THREE.PointCloudMaterial(materialOptions);

		// The wizard gaze became stern, his jaw set, he creates the cosmos with a wave of his arms

		for (var i = 0; i < starQty; i++) {		

			var starVertex = new THREE.Vector3();
			starVertex.x = Math.random() * 2000 - 1000;
			starVertex.y = Math.random() * 2000 - 1000;
			starVertex.z = Math.random() * 2000 - 1000;

			geometry.vertices.push(starVertex);
			
		}


		stars = new THREE.PointCloud(geometry, starStuff);
		scene.add(stars);
		//
		//var time = Date.now() * 0.0004;
		//stars.rotation.y=time;
		TweenMax.to(stars.rotation, 6000,{y:360,ease:Linear.easeInOut,repeat:-1});
		TweenMax.to(stars.rotation, 12000,{x:360,ease:Linear.easeInOut,repeat:-1});
		//stars.rotation.z=time*0.7;
	};//star
	
	
	