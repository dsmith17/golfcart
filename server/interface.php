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
               <div class="cellpad"><input type="image" src="imgs/arrows-up.png" alt="submit" name="clickme" value="up"><br>
                    <input type="image" src="imgs/arrows-down.png" alt="submit" name="clickme" value="down"></div>
               <div class="cellpad">
                    <input type="image" src="imgs/Stop_square_scaled.png" alt="submit" name="clickme" value="stop"><br>
                    <div class="wrapper">
                         <input type="image" src="imgs/Reset_square_scaled.png" alt="submit" name="clickme" value="reset"><br>
                         <input type="image" src="imgs/Refresh_square_scaled.png" alt="submit" name="clickme" value="reload"><br>
                         <input type="image" src="imgs/ChangeDirections_square_scaled.png" alt="submit" name="clickme" value="change_direction">
                    </div>
               </div>
               <div class="cellpad">
                         <input type="image" src="imgs/arrows-left.png" alt="submit" name="clickme" value="left">
               </div>
               <div class="cellpad">
                    <input class="cellcenter" type="image" src="imgs/arrows-right.png" alt="submit" name="clickme" value="right">
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
	</div><!-- end of rowGroup -->
</div>   
</form>

</body>
</html>

<?php
}

?>
