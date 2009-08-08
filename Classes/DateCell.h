//
//  DateCell.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 07/06/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <Foundation/Foundation.h>

#import "SwitchCell.h"

@interface DateCell : SwitchCell
{
	UILabel *dateLabel;
}

@property (nonatomic, retain) IBOutlet UILabel *dateLabel;

- (void)setDate:(NSString *)date;

@end
