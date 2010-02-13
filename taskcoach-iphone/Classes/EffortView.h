//
//  EffortView.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 30/01/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import <UIKit/UIKit.h>

@class Task;

@interface EffortView : UITableViewController
{
	Task *task;
	NSMutableArray *efforts;
}

- initWithTask:(Task *)task;

@end
