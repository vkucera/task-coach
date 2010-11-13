//
//  ConfigurationView.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 23/10/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import <UIKit/UIKit.h>

#import "SwitchCell.h"
#import "RecurrencePeriodCell.h"

@interface ConfigurationView : UITableViewController <SwitchCellDelegate, RecurrencePeriodCellDelegate>
{
	NSMutableArray *cells;
	id target;
	SEL action;
	NSInteger firstSec;
}

- init;
- (void)setTarget:(id)target action:(SEL)action;

@end
