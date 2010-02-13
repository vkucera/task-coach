//
//  CellFactory.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 17/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "CellFactory.h"

#import "TaskCell.h"
#import "TextFieldCell.h"
#import "SwitchCell.h"
#import "DateCell.h"
#import "DescriptionCell.h"
#import "BadgedCell.h"
#import "ButtonCell.h"

#import "Configuration.h"

static CellFactory *_cellFactory = NULL;

@implementation CellFactory

@synthesize taskCellTemplate;
@synthesize textFieldCellTemplate;
@synthesize switchCellTemplate;
@synthesize dateCellTemplate;
@synthesize descriptionCellTemplate;
@synthesize badgedCellTemplate;
@synthesize buttonCellTemplate;

+ (CellFactory *)cellFactory
{
	if (!_cellFactory)
		_cellFactory = [[CellFactory alloc] init];
	return _cellFactory;
}

- (TaskCell *)createTaskCell
{
	if ([Configuration configuration].iconPosition == ICONPOSITION_RIGHT)
	{
		if ([Configuration configuration].compactTasks)
			[[NSBundle mainBundle] loadNibNamed:@"TaskCellRight" owner:self options:nil];
		else
			[[NSBundle mainBundle] loadNibNamed:@"TaskCellRightBig" owner:self options:nil];
	}
	else
	{
		if ([Configuration configuration].compactTasks)
			[[NSBundle mainBundle] loadNibNamed:@"TaskCellLeft" owner:self options:nil];
		else
			[[NSBundle mainBundle] loadNibNamed:@"TaskCellLeftBig" owner:self options:nil];
	}
	
	return [taskCellTemplate retain];
}

- (TextFieldCell *)createTextFieldCell
{
	[[NSBundle mainBundle] loadNibNamed:@"TextFieldCell" owner:self options:nil];
	return textFieldCellTemplate;
}

- (SwitchCell *)createSwitchCell
{
	[[NSBundle mainBundle] loadNibNamed:@"SwitchCell" owner:self options:nil];
	return switchCellTemplate;
}

- (DateCell *)createDateCell
{
	[[NSBundle mainBundle] loadNibNamed:@"DateCell" owner:self options:nil];
	return dateCellTemplate;
}

- (DescriptionCell *)createDescriptionCell
{
	[[NSBundle mainBundle] loadNibNamed:@"DescriptionCell" owner:self options:nil];
	return descriptionCellTemplate;
}

- (BadgedCell *)createBadgedCell
{
	[[NSBundle mainBundle] loadNibNamed:@"BadgedCell" owner:self options:nil];
	return [badgedCellTemplate retain];
}

- (ButtonCell *)createButtonCell
{
	[[NSBundle mainBundle] loadNibNamed:@"ButtonCell" owner:self options:nil];
	return [buttonCellTemplate retain];
}

@end
