//
//  CellFactory.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 17/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "CellFactory.h"

#import "TaskCell.h"

static CellFactory *_cellFactory = NULL;

@implementation CellFactory

@synthesize taskCellTemplate;

+ (CellFactory *)cellFactory
{
	if (!_cellFactory)
		_cellFactory = [[CellFactory alloc] init];
	return _cellFactory;
}

- (TaskCell *)createTaskCell
{
	[[NSBundle mainBundle] loadNibNamed:@"TaskCell" owner:self options:nil];
	return [taskCellTemplate retain];
}

@end
