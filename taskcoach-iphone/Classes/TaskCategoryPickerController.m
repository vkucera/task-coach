//
//  TaskCategoryPickerController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 02/08/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "TaskCategoryPickerController.h"
#import "Task.h"
#import "BadgedCell.h"

@implementation TaskCategoryPickerController

- initWithTask:(Task *)task
{
	if (self = [super initWithNibName:@"TaskCategoryPicker" bundle:[NSBundle mainBundle]])
	{
		myTask = [task retain];
	}
	
	return self;
}

- (void)dealloc
{
	[myTask release];
	
	[super dealloc];
}

- (void)fillCell:(BadgedCell *)cell forCategory:(Category *)category
{
	[super fillCell:cell forCategory:category];
	
	if ([myTask hasCategory:category])
	{
		cell.accessoryType = UITableViewCellAccessoryCheckmark;
	}
}

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath
{
	Category *category = [categories objectAtIndex:indexPath.row];
	UITableViewCell *cell = [self.tableView cellForRowAtIndexPath:indexPath];
	
	if ([myTask hasCategory:category])
	{
		[myTask removeCategory:category];
		cell.accessoryType = UITableViewCellAccessoryNone;
	}
	else
	{
		[myTask addCategory:category];
		cell.accessoryType = UITableViewCellAccessoryCheckmark;
	}
	
	[self.tableView deselectRowAtIndexPath:indexPath animated:YES];
}

@end
