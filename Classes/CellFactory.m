//
//  CellFactory.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 17/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "CellFactory.h"

#import "TaskCell.h"
#import "TextFieldCell.h"
#import "SwitchCell.h"

#import "Configuration.h"

static CellFactory *_cellFactory = NULL;

@implementation CellFactory

@synthesize taskCellTemplate;
@synthesize textFieldCellTemplate;
@synthesize switchCellTemplate;

+ (CellFactory *)cellFactory
{
	if (!_cellFactory)
		_cellFactory = [[CellFactory alloc] init];
	return _cellFactory;
}

- (TaskCell *)createTaskCell
{
	if ([Configuration configuration].iconPosition == ICONPOSITION_RIGHT)
		[[NSBundle mainBundle] loadNibNamed:@"TaskCellRight" owner:self options:nil];
	else
		[[NSBundle mainBundle] loadNibNamed:@"TaskCellLeft" owner:self options:nil];

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

@end
