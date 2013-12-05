<?php
function interface_header()
{
?>

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<title>Controls</title>
<style type="text/css">
/*used to make a div look like a table*/
.table
{
     display:table;
     border-collapse:collapse;
}
.header
{
     display:table-header-group;
     font-weight:bold;
     text-align:center;
}
.rowGroup
{
     display:table-row-group;
}
.row
{
     display:table-row;
}
.cell 
{
     display:table-cell;
     border-style:solid;
     border-width:1px;
     
     padding:3px;
}
.cellpad 
{
     display:table-cell;
     padding:10px;
     vertical-align: middle;
}

.wrapper 
{
     text-align: center;
}

input.up
{
     background:url(imgs/arrows-up.png) no-repeat;
     width:    154px;
     height:   201px;
     border:   none;
     cursor:   pointer;
     display:  block;
     text-indent:   -3000px;
}

input.down
{
     background:url(imgs/arrows-down.png) no-repeat;
     width:    154px;
     height:   201px;
     border:   none;
     cursor:   pointer;
     display:  block;
     text-indent:   -3000px;
}

input.stop
{
     background:url(imgs/Stop_square_scaled.png) no-repeat;
     width:    150px;
     height:   71px;
     border:   none;
     cursor:   pointer;
/*      display:  block; */
     text-indent:   -3000px;
}

input.reset
{
     background:url(imgs/Reset_square_scaled.png) no-repeat;
     width:    150px;
     height:   71px;
     border:   none;
     cursor:   pointer;
/*      display:  block; */
     text-indent:   -3000px;
}

input.refresh
{
     background:url(imgs/Refresh_square_scaled.png) no-repeat;
     width:    150px;
     height:   71px;
     border:   none;
     cursor:   pointer;
/*      display:  block; */
     text-indent:   -3000px;
}

input.changedirection
{
     background:url(imgs/ChangeDirections_square_scaled.png) no-repeat;
     width:    150px;
     height:   71px;
     border:   none;
     cursor:   pointer;
     display:  block;
     text-indent:   -3000px;
}

input.left
{
     background:url(imgs/arrows-left.png) no-repeat;
     width:    200px;
     height:   154px;
     border:   none;
     cursor:   pointer;
     display:  block;
     text-indent:   -3000px;
}

input.right
{
     background:url(imgs/arrows-right.png) no-repeat;
     width:    200px;
     height:   154px;
     border:   none;
     cursor:   pointer;
     display:  block;
     text-indent:   -3000px;
}




</style>
</head>
<body>

<form name="controls1" enctype="multipart/form-data" method="POST" action="index.php">
<?php
}

function interface_controls()
{
?>
<hr>

<div class="table">
     <div class="rowGroup">
          <div class="row">
               <div class="cellpad">
                    <input class="up" type="submit" name="clickme" value="up"><br>
                    <input class="down" type="submit" name="clickme" value="down">
               </div>
               <div class="cellpad">
                    <input class="stop" type="submit" name="clickme" value="stop"><br>
                    <div class="wrapper">
                         <input class="reset" type="submit" name="clickme" value="reset"><br>
                         <input class="refresh" type="submit" name="clickme" value="reload"><br>
                         <input class="changedirection" type="submit" name="clickme" value="change_direction">
                    </div>
               </div>
               <div class="cellpad">
                         <input class="left" type="submit" name="clickme" value="left">
               </div>
               <div class="cellpad">
<!--                     <input class="cellcenter" type="image" src="imgs/arrows-right.png" alt="submit" name="clickme" value="right"> -->
                         <input class="right" type="submit" name="clickme" value="right">
               </div>
          </div><!-- end of the row -->
     </div><!-- end of rowGroup -->
</div> <!-- end table --> 

<div class="table">
	<input type="hidden" name="MAXFILESIZE" value="1000000">
	<div class="rowGroup">
		<div class="row">
			<div class="cellpad">
				<input type="submit" name="clickme" value="script" >
			</div>
			<div class="cellpad">
				<input name="THE_SCRIPT" type="file" size="30">
			</div>
			<div class="cellpad">
				<input type="submit" name="clickme" value="upload" >
			</div>
		</div><!-- end row -->
		<div class="row">
			<div class="cellpad">
				<input type="submit" name="clickme" value="steer_mode">
			</div>			
		</div>
	</div><!-- end of rowGroup -->
</div>   
</form>

</body>
</html>

<?php
}

?>
